import streamlit as st
import re
import pandas as pd

# Fonction pour générer automatiquement la documentation d'une expression régulière
def generer_documentation(pattern):
    """Analyse une expression régulière et génère une documentation explicative détaillée."""
    try:
        doc = []
        exemples_valides = []
        exemples_invalides = []
        
        # Analyse basique du pattern
        if pattern.startswith('^') and pattern.endswith('$'):
            doc.append("Cette expression régulière valide une chaîne complète (doit correspondre du début à la fin).")
        elif pattern.startswith('^'):
            doc.append("Cette expression régulière valide le début d'une chaîne.")
        elif pattern.endswith('$'):
            doc.append("Cette expression régulière valide la fin d'une chaîne.")
        else:
            doc.append("Cette expression régulière recherche un motif n'importe où dans la chaîne.")
        
        # Reconnaissance de motifs spécifiques avec interprétation détaillée
        if pattern == r'^[A-Z][A-Z\s\-\']*$':
            doc = ["Cette expression régulière valide un nom écrit entièrement en MAJUSCULES."]
            doc.append("La chaîne doit commencer par une lettre majuscule ([A-Z]).")
            doc.append("Elle peut ensuite contenir plusieurs (ou aucun) caractères parmi: lettres majuscules, espaces, tirets ou apostrophes ([A-Z\\s\\-\']*).")
            doc.append("Aucun autre caractère n'est autorisé (chiffres, minuscules, symboles, etc.).")
            exemples_valides = ["DUPONT", "MARTIN-DURAND", "O'CONNOR", "DE LA FONTAINE"]
            exemples_invalides = ["Dupont", "MARTIN2", "dupont", "123NOM"]
        
        elif r'^[0-9]{9}[A-Z]{2}$' in pattern:
            doc = ["Cette expression régulière valide un code INE (Identifiant National Étudiant)."]
            doc.append("La chaîne doit contenir exactement 9 chiffres ([0-9]{9}) suivis de 2 lettres majuscules ([A-Z]{2}).")
            doc.append("Aucun espace ou autre caractère n'est autorisé.")
            exemples_valides = ["123456789AB", "987654321XY"]
            exemples_invalides = ["12345678AB", "123456789abc", "ABC123456", "123456789A"]
        
        elif r'^\d{2}-\d{2}-\d{4}$' in pattern:
            doc = ["Cette expression régulière valide une date au format JJ-MM-AAAA."]
            doc.append("La chaîne doit contenir exactement 2 chiffres (jour), suivis d'un tiret, de 2 chiffres (mois), d'un tiret, puis de 4 chiffres (année).")
            doc.append("Tous les chiffres doivent être sur 2 positions pour les jours et mois, et sur 4 positions pour l'année.")
            doc.append("Le séparateur doit être un tiret (-) et non un autre caractère.")
            exemples_valides = ["01-01-2023", "31-12-2022"]
            exemples_invalides = ["1-1-2023", "01/01/2023"]
        
        elif r'^(0[1-9]|1[0-2])\/20[0-9]{2}$' in pattern:
            doc = ["Cette expression régulière valide une date au format MM/AAAA pour le 21ème siècle (2000-2099)."]
            doc.append("Le mois doit être compris entre 01 et 12 (0[1-9] ou 1[0-2]).")
            doc.append("Le séparateur doit être un slash (/).")
            doc.append("L'année doit commencer par '20' suivi de deux chiffres (entre 2000 et 2099).")
            exemples_valides = ["01/2023", "12/2099", "05/2010"]
            exemples_invalides = ["1/2023", "13/2023", "05/123", "05-2023", "05/1999"]
        
        elif r'@' in pattern and r'\.' in pattern:
            doc.append("Elle semble valider un format d'adresse email.")
            doc.append("Elle recherche un caractère '@' suivi d'un domaine contenant un point.")
            exemples_valides = ["exemple@domaine.com", "prenom.nom@entreprise.fr"]
            exemples_invalides = ["exemple@", "exemple@domaine", "@domaine.com"]
        
        # Si on n'a pas reconnu précisément le motif, faire une analyse plus générique
        if len(doc) <= 2:
            # Analyse détaillée des classes de caractères
            if '[A-Z]' in pattern:
                doc.append("Elle contient des lettres majuscules (A à Z).")
            if '[a-z]' in pattern:
                doc.append("Elle contient des lettres minuscules (a à z).")
            if '[0-9]' in pattern:
                doc.append("Elle contient des chiffres (0 à 9).")
            
            # Analyse détaillée des motifs courants
            if r'\d' in pattern:
                doc.append("Elle contient des chiffres (\\d équivaut à [0-9]).")
            if r'\w' in pattern:
                doc.append("Elle contient des caractères alphanumériques (lettres, chiffres, underscore).")
            if r'\s' in pattern:
                doc.append("Elle contient des espaces blancs (espaces, tabulations, retours à la ligne, etc.).")
            
            # Analyse des quantificateurs spécifiques
            if '*' in pattern:
                doc.append("Elle contient un élément qui peut se répéter zéro ou plusieurs fois (*).")
            if '+' in pattern:
                doc.append("Elle contient un élément qui doit se répéter une ou plusieurs fois (+).")
            if '?' in pattern:
                doc.append("Elle contient un élément optionnel (?).")
            
            # Analyse des séquences spécifiques (séquences d'échappement)
            if r'\-' in pattern or r"\\'" in pattern:
                doc.append("Elle contient des caractères spéciaux échappés (comme tiret ou apostrophe).")
                
            # Analyse plus détaillée des classes de caractères
            if '[' in pattern and ']' in pattern:
                import re
                # Analyser les classes de caractères complexes
                classes = re.findall(r'\[(.*?)\]', pattern)
                for classe in classes:
                    if '-' in classe:
                        # Tenter de décrire les plages
                        plages = []
                        if 'A-Z' in classe:
                            plages.append("lettres majuscules (A-Z)")
                        if 'a-z' in classe:
                            plages.append("lettres minuscules (a-z)")
                        if '0-9' in classe:
                            plages.append("chiffres (0-9)")
                        if plages:
                            doc.append(f"Elle contient une classe de caractères incluant: {', '.join(plages)}.")
                    
                    # Caractères spécifiques
                    special_chars = {'\\s': 'espaces', '\\d': 'chiffres', '\\w': 'caractères de mot'}
                    for char, desc in special_chars.items():
                        if char in classe:
                            doc.append(f"Elle accepte des {desc} dans une classe de caractères.")
            
            # Analyse des groupes et alternatives
            if '(' in pattern and ')' in pattern:
                import re
                # Trouver les groupes pour analyse
                groupes = re.findall(r'\((.*?)\)', pattern)
                if groupes:
                    doc.append(f"Elle contient {len(groupes)} groupe(s) de capture pour extraire des parties spécifiques du texte.")
                    # Si un groupe contient un | (alternative)
                    for groupe in groupes:
                        if '|' in groupe:
                            alternatives = groupe.split('|')
                            doc.append(f"Elle contient une alternative entre plusieurs options: {', '.join([f'`{alt}`' for alt in alternatives])}.")
            
            # Analyse des quantificateurs précis
            quantif_pattern = re.compile(r'\{(\d+)(?:,(\d+)?)?\}')
            quantifs = quantif_pattern.findall(pattern)
            for quantif in quantifs:
                if quantif[1]:  # {n,m}
                    doc.append(f"Elle impose entre {quantif[0]} et {quantif[1]} occurrences d'un élément.")
                else:  # {n}
                    doc.append(f"Elle impose exactement {quantif[0]} occurrences d'un élément.")
        
        # Construire la documentation finale
        documentation = "\n".join(doc)
        
        if exemples_valides:
            documentation += "\n\nExemples valides :\n"
            documentation += "\n".join([f"- {ex}" for ex in exemples_valides])
            
        if exemples_invalides:
            documentation += "\n\nExemples invalides :\n"
            documentation += "\n".join([f"- {ex}" for ex in exemples_invalides])
            
        if not exemples_valides and not exemples_invalides:
            documentation += "\n\nNote : Vous pouvez enrichir cette documentation en ajoutant vos propres exemples valides et invalides."
        
        return documentation
    
    except Exception as e:
        return f"Impossible de générer la documentation automatiquement : {str(e)}\n\nVeuillez décrire manuellement ce que fait cette expression régulière."

# Configuration de la page
st.set_page_config(page_title="one trick RegEx", page_icon="🦄", layout="wide")

# Titre principal de l'application
st.title("One trick RegEx")

# Interface divisée en deux colonnes
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Créer votre expression régulière (RegEx)")
    
    # Zone de saisie du regex
    default_pattern = r"^\d{2}-\d{2}-\d{4}$"
    # Utiliser la valeur de session_state si elle existe, sinon utiliser la valeur par défaut
    regex_pattern = st.text_input("Entrez votre expression régulière:", 
                              value=st.session_state.get('regex_pattern', default_pattern),
                              help=r"Exemple: ^\d{2}-\d{2}-\d{4}$ pour valider une date au format JJ-MM-AAAA")

    # Description du regex
    st.subheader("Explication")
    
    # Ajout d'un bouton pour générer la documentation automatiquement
    if st.button("Générer une explication automatique"):
        doc_generee = generer_documentation(regex_pattern)
        st.session_state['documentation_generee'] = doc_generee
    
    # Utiliser la documentation générée si disponible, sinon utiliser la valeur par défaut
    documentation_defaut = "Cette expression régulière valide une date au format JJ-MM-AAAA.\n\nExemples valides :\n- 01-01-2023\n- 31-12-2022\n\nExemples invalides :\n- 1-1-2023 (les chiffres doivent être sur 2 positions)\n- 01/01/2023 (mauvais séparateur)"
    regex_description = st.text_area(
        "Décrivez ce que fait votre expression régulière:", 
        height=150,
        value=st.session_state.get('documentation_generee', documentation_defaut)
    )

with col2:
    st.subheader("Tester votre expression régulière")
    
    # Zone de test avec plusieurs lignes
    test_strings = st.text_area(
        "Entrez des textes à tester (un par ligne):",
        height=150,
        value="01-01-2023\n31-12-2022\n1-1-2023\n01/01/2023\nABC"
    )
    
    # Bouton pour tester
    test_button = st.button("Tester", type="primary")
    
    # Tester le regex quand on clique sur le bouton
    if test_button:
        try:
            # Récupérer les flags depuis les options en bas de page
            current_flags = 0
            if 'ignore_case' in st.session_state and st.session_state['ignore_case']:
                current_flags |= re.IGNORECASE
            if 'multiline' in st.session_state and st.session_state['multiline']:
                current_flags |= re.MULTILINE
            if 'dotall' in st.session_state and st.session_state['dotall']:
                current_flags |= re.DOTALL
            if 'verbose' in st.session_state and st.session_state['verbose']:
                current_flags |= re.VERBOSE
                
            # Compiler le regex avec les flags
            pattern = re.compile(regex_pattern, flags=current_flags)
            
            # Tester chaque ligne
            results = []
            for i, line in enumerate(test_strings.splitlines()):
                if not line.strip():  # Ignorer les lignes vides
                    continue
                    
                match = pattern.search(line)
                
                # Récupérer les groupes si disponibles
                groups = match.groups() if match else None
                group_dict = match.groupdict() if match else None
                
                results.append({
                    "Ligne": i+1,
                    "Texte": line,
                    "Correspond": "✓" if match else "✗",
                    "Valeur trouvée": match.group(0) if match else None,
                    "Groupes": str(groups) if groups else None,
                    "Groupes nommés": str(group_dict) if group_dict and len(group_dict) > 0 else None
                })
            
            # Afficher les résultats dans un tableau
            if results:
                # Configuration des styles pour le tableau
                # Colorer les symboles ✓ en vert et ✗ en rouge
                df = pd.DataFrame(results)
                
                # Formatter le tableau
                def highlight_match(val):
                    if val == "✓":
                        return 'color: green; font-weight: bold'
                    elif val == "✗":
                        return 'color: red; font-weight: bold'
                    else:
                        return ''
                
                # Appliquer le style
                styled_df = df.style.map(highlight_match, subset=['Correspond'])
                
                # Afficher le tableau avec style
                st.dataframe(styled_df, use_container_width=True)
                
                # Résumé avec coloration
                matches_count = sum(1 for r in results if r["Correspond"] == "✓")
                if matches_count > 0:
                    st.success(f"{matches_count} correspondance(s) trouvée(s) sur {len(results)} ligne(s).")
                else:
                    st.error(f"0 correspondance trouvée sur {len(results)} ligne(s).")
            else:
                st.warning("Aucun texte à tester.")
            
        except Exception as e:
            st.error(f"Erreur lors de l'exécution du regex: {str(e)}")

# Section avec exemples courants
st.markdown("---")
with st.expander("**Exemples d'expressions régulières courantes**"):
    examples = {
        "Nom en majuscules": {
            "regex": r"^[A-Z][A-Z\s\-']*$",
            "description": "Valide un nom écrit entièrement en majuscules, avec espaces, tirets ou apostrophes.",
            "exemples_valides": ["DUPONT", "MARTIN-DURAND", "O'CONNOR", "DE LA FONTAINE"],
            "exemples_invalides": ["Dupont", "MARTIN2", "dupont", "123NOM"]
        },
        "Code INE": {
            "regex": r"^[0-9]{9}[A-Z]{2}$",
            "description": "Valide un code INE (Identifiant National Étudiant) composé de 9 chiffres suivis de 2 lettres majuscules.",
            "exemples_valides": ["123456789AB", "987654321XY"],
            "exemples_invalides": ["12345678AB", "123456789abc", "ABC123456", "123456789A"]
        },
        "Format date mois/année": {
            "regex": r"^(0[1-9]|1[0-2])\/20[0-9]{2}$",
            "description": "Valide une date au format MM/AAAA pour le 21ème siècle (2000-2099).",
            "exemples_valides": ["01/2023", "12/2099", "05/2010"],
            "exemples_invalides": ["1/2023", "13/2023", "05/123", "05-2023", "05/1999"]
        }
    }
    
    # Afficher chaque exemple
    for name, example in examples.items():
        st.subheader(name)
        st.code(example["regex"])
        st.write(example["description"])
        st.write("**Exemples valides:** " + ", ".join(f"`{ex}`" for ex in example["exemples_valides"]))
        st.write("**Exemples invalides:** " + ", ".join(f"`{ex}`" for ex in example["exemples_invalides"]))
        
        # Créer un bouton pour utiliser cet exemple
        if st.button(f"Utiliser cet exemple ({name})"):
            st.session_state['regex_pattern'] = example["regex"]
            st.rerun()
        
        st.markdown("---")


# Section explicative sur les expressions régulières
with st.expander("Guide des expressions régulières"):
    st.markdown("""
    ## Aide-mémoire sur les expressions régulières
    
    ### Métacaractères de base
    - `.` : N'importe quel caractère sauf nouvelle ligne
      * Exemple: `a.c` correspond à "abc", "adc", "a1c", etc.
    - `^` : Début de chaîne
      * Exemple: `^bonjour` correspond à "bonjour monde" mais pas à "mon bonjour"
    - `$` : Fin de chaîne
      * Exemple: `monde$` correspond à "bonjour monde" mais pas à "monde entier"
    - `*` : 0 ou plusieurs occurrences
      * Exemple: `ab*c` correspond à "ac", "abc", "abbc", "abbbc", etc.
    - `+` : 1 ou plusieurs occurrences
      * Exemple: `ab+c` correspond à "abc", "abbc", "abbbc", mais pas à "ac"
    - `?` : 0 ou 1 occurrence
      * Exemple: `colou?r` correspond à "color" et "colour"
    - `{n}` : Exactement n occurrences
      * Exemple: `a{3}` correspond à "aaa" mais pas à "aa" ou "aaaa"
    - `{n,}` : Au moins n occurrences
      * Exemple: `a{2,}` correspond à "aa", "aaa", "aaaa", etc. mais pas à "a"
    - `{n,m}` : Entre n et m occurrences
      * Exemple: `a{2,4}` correspond à "aa", "aaa", "aaaa" mais pas à "a" ou "aaaaa"
    """)
    
    st.markdown("""
    ### Classes de caractères
    - `[abc]` : Un des caractères a, b ou c
      * Exemple: `[aeiou]` correspond à n'importe quelle voyelle
    - `[^abc]` : Tout caractère sauf a, b et c
      * Exemple: `[^0-9]` correspond à tout caractère qui n'est pas un chiffre
    - `[a-z]` : Tout caractère entre a et z
      * Exemple: `[a-z]` correspond à toute lettre minuscule de l'alphabet latin
    - `\\d` : Chiffre (`[0-9]`)
      * Exemple: `\\d{3}` correspond à trois chiffres comme "123", "456"
    - `\\D` : Non-chiffre (`[^0-9]`)
      * Exemple: `\\D+` correspond à une suite de caractères sans chiffres
    - `\\w` : Caractère de mot (`[a-zA-Z0-9_]`)
      * Exemple: `\\w+` correspond à un mot comme "exemple_123"
    - `\\W` : Non-caractère de mot
      * Exemple: `\\W` correspond à des caractères comme "!", "@", "#"
    - `\\s` : Espace blanc
      * Exemple: `mot\\ssuivant` correspond à "mot suivant"
    - `\\S` : Non-espace blanc
      * Exemple: `\\S+` correspond à une suite de caractères sans espaces
    """)
    
    st.markdown("""
    ### Groupes
    - `(...)` : Capture un groupe
      * Exemple: `(\\d{2})-(\\d{2})-(\\d{4})` capture jour, mois et année
    - `(?:...)` : Groupe non capturant
      * Exemple: `(?:https?://)?example\\.com` groupe optionnel sans capture
    - `(?P<name>...)` : Groupe nommé
      * Exemple: `(?P<jour>\\d{2})-(?P<mois>\\d{2})-(?P<annee>\\d{4})`
    
    ### Alternatives
    - `a|b` : a ou b
      * Exemple: `chat|chien` correspond à "chat" ou "chien"
    """)

# Accordéon avec options du regex - placé tout en bas de la page
st.markdown("---")
with st.expander("Options avancées"):
    st.write("Ces options modifient le comportement de l'expression régulière:")
    col_options1, col_options2 = st.columns(2)
    with col_options1:
        st.session_state['ignore_case'] = st.checkbox("Ignorer la casse (re.IGNORECASE)", 
                                                   value=st.session_state.get('ignore_case', False))
        st.session_state['multiline'] = st.checkbox("Mode multiligne (re.MULTILINE)", 
                                                 value=st.session_state.get('multiline', False))
    with col_options2:
        st.session_state['dotall'] = st.checkbox("Point correspond à tout (re.DOTALL)", 
                                              value=st.session_state.get('dotall', False))
        st.session_state['verbose'] = st.checkbox("Mode verbose (re.VERBOSE)", 
                                               value=st.session_state.get('verbose', False))
    
    # Explication détaillée des options
    st.markdown("""
    #### Détails des options
    
    - **Ignorer la casse** : Rend le regex insensible à la casse. Ex: `/abc/i` correspond à "ABC", "abc", "Abc", etc.
    - **Mode multiligne** : Fait que `^` et `$` correspondent au début/fin de chaque ligne, pas seulement au début/fin du texte.
    - **Point correspond à tout** : Fait que le caractère `.` correspond également aux sauts de ligne `\\n`.
    - **Mode verbose** : Permet d'écrire des regex plus lisibles avec des espaces et commentaires ignorés.
    """)

# Mise à jour de la variable de session
if 'regex_pattern' in st.session_state:
    if st.session_state['regex_pattern'] != regex_pattern:
        st.session_state['regex_pattern'] = regex_pattern
