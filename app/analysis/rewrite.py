def anti_clickbait_title(title: str) -> str:
    t = title
    repl = {
        "Tu ne devineras jamais": "Voici ce qu'on a appris",
        "Tu ne devineras": "Voici ce qu'on a appris",
        "Incroyable": "Concret",
        "Secret": "Méthode"
    }
    for k,v in repl.items():
        t = t.replace(k, v)
    return (t[:78] + "…") if len(t) > 80 else t

def anti_clickbait_desc(desc: str) -> str:
    d = desc
    d = d.replace("Commente OUI si tu veux la suite", "Dites-moi ce que vous en pensez")
    d = d.replace("Partage maintenant", "À garder sous la main")
    return d[:220]

def inform_block(needs: bool, links=None) -> str:
    if not needs:
        return ""
    links = links or []
    src = " | ".join(links[:3]) if links else "sources à préciser"
    return f"Contexte & sources: {src}. Transparence: contenu édité et vérifié manuellement."
