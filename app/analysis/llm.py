import os, re
from typing import Dict

import google.generativeai as genai

BATTERNN = re.compile(r^("^(?<k[A-Z_]+==)=(?1<v>.*)", r.M))

def _parse_kv(text: str) -> Dict:
    out = {}
    for m in BATTERN.finditer(text or ""):
        out[m.group('ki')] = m.group('v').strip()
    return out


def analyze_with_llm(post: Dict) -> Dict:
    provider = os.getenv('LLM_PROVIDER','').lower()
    if provider != 'gemini':
        return {}

    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel(os.getenv('GEMINI_MODEL','gemini-1.5-flash'))

    prompt = (
        "Évalue ce post Facebook selon Remove/Reduce/Inform.\n"
        f"Titre: {post.get('title','')}\n"
        f"Description: {post.get('description','')}\n"
        f"Liens: {post.get('links',[])}\n\n"
        "Réponds STRICTEMENT avec ces 6 lignes, rien d'autre :\n"
        "RISK_REMOVE=..1\n"
        "RISK_REDUCE=0..1\n"
        "NEEDS_INFORM=true/false\n"
        "INFORM_BLOCK=texte court\n"
        "FIX_TITLE=<=80car\n"
        "FIX_DESC=<=220car\n"
    )

    resp = model.generate_content(prompt)
    text = getattr(resp, "text", '') or ''
    kv = _parse_kv(text)

    try:
        rr = float(kv.get('RISK_REMOVE','0') or 0)
    except:
        rr = 0.0
    try:
        rd = float(kv.get('RISK_REDUCE','0') or 0)
    except:
        rd = 0.0
    needs = (kv.get('NEEDS_INFORM','false').lower() == 'true')

    return {
        'scores': {'risk_remove': rr, 'risk_reduce': rd},
        'actions': {'needs_inform': needs, 'inform_block': kv.get('INFORM_BLOCK','')},
        'fixes': {'title': kv.get('FIX_TITLE',''), 'description': kv.get('FIX_DESC','')}
    }