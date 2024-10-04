import spacy
import pandas as pd
import streamlit as st
import PyPDF2
import plotly.express as px
import plotly.graph_objects as go



# Titre de l'application
st.title("Auto_Tri_CV")

# Charger le modèle de langue
nlp = spacy.load("en_core_web_sm")

# Liste de compétences à détecter
competences_liste = ["Python", "Machine Learning", "Data Analysis", "SQL", "Java", "Project Management"]

# Fonction pour extraire les compétences d'un texte
def extraire_competences(cv_text):
    found_skills = [skill for skill in competences_liste if skill.lower() in cv_text.lower()]
    return found_skills

# Fonction pour extraire le texte des fichiers PDF
def extraire_texte_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    texte = ""
    for page_num in range(len(pdf_reader.pages)):
        texte += pdf_reader.pages[page_num].extract_text()
    return texte

# Mots-clés pour détecter les années d'expérience et le niveau d'éducation
mots_cles_experience = ["years of experience", "experience", "worked at", "positions", "role"]
mots_cles_education = ["degree", "bachelor", "master", "PhD", "graduated", "BSc", "MSc", "doctoral"]

# Fonction pour extraire l'expérience d'un texte
def extraire_experience(cv_text):
    doc = nlp(cv_text)
    experience = []
    for sentence in doc.sents:
        if any(keyword in sentence.text.lower() for keyword in mots_cles_experience):
            experience.append(sentence.text)
    return experience

# Fonction pour extraire le niveau d'éducation d'un texte
def extraire_education(cv_text):
    doc = nlp(cv_text)
    education = []
    for sentence in doc.sents:
        if any(keyword in sentence.text.lower() for keyword in mots_cles_education):
            education.append(sentence.text)
    return education

# Pondération pour les critères
poids_competences = 0.5
poids_experience = 0.3
poids_education = 0.2

# Calcul du score final basé sur les pondérations
def calculer_score(competences, experience, education):
    score_competences = len(competences)
    score_experience = len(experience)
    score_education = len(education)
    
    score_total = (score_competences * poids_competences + 
                   score_experience * poids_experience + 
                   score_education * poids_education)
    return score_total

# Interface utilisateur pour télécharger les CV
uploaded_files = st.file_uploader("Télécharger les CV", accept_multiple_files=True, type=["txt", "pdf"])

cv_data = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        # Traiter les fichiers PDF et TXT
        if uploaded_file.type == "application/pdf":
            cv_text = extraire_texte_pdf(uploaded_file)
        else:
            cv_text = uploaded_file.read().decode("utf-8")
        
        # Extraire les compétences, expérience et éducation
        competences = extraire_competences(cv_text)
        experience = extraire_experience(cv_text)
        education = extraire_education(cv_text)
        
        # Calculer le score avec pondération
        score = calculer_score(competences, experience, education)
        
        # Ajouter les informations au tableau
        cv_data.append({
            "CV": uploaded_file.name,
            "Compétences": competences,
            "Expérience": experience,
            "Éducation": education,
            "Score": score
        })

# Convertir en DataFrame pour visualisation
if cv_data:
    df_cv = pd.DataFrame(cv_data)

# Menu de navigation dans la barre latérale
menu = st.sidebar.selectbox("Menu", ["Accueil", "Classement des CV", "Visualisation des Compétences", "Visualisation des Scores"])

# Logique de navigation
if menu == "Accueil":
    st.write("Bienvenue sur l'application Auto_Tri_CV. Téléchargez des CV pour commencer.")

elif menu == "Classement des CV" and cv_data:
    st.write("CV classés par score :")
    df_sorted = df_cv.sort_values(by="Score", ascending=False)
    st.dataframe(df_sorted)
    
    # Option d'exportation des résultats sous forme CSV
    csv = df_sorted.to_csv(index=False).encode('utf-8')
    st.download_button(label="Télécharger les résultats", data=csv, file_name="classement_cv.csv", mime="text/csv")

elif menu == "Visualisation des Compétences" and cv_data:
    st.write("Visualisation de la répartition des compétences.")
    
    # Créer un histogramme des compétences avec Plotly
    all_competences = [skill for sublist in df_cv["Compétences"] for skill in sublist]
    if all_competences:
        competence_count = pd.Series(all_competences).value_counts()
        
        fig = px.bar(
            competence_count, 
            x=competence_count.values, 
            y=competence_count.index, 
            labels={'x': 'Nombre d\'occurrences', 'index': 'Compétences'},
            title="Répartition des compétences"
        )
        st.plotly_chart(fig)

elif menu == "Visualisation des Scores" and cv_data:
    st.write("Distribution des scores des CV.")
    
    # Créer une visualisation des scores avec Plotly
    fig = px.histogram(
        df_cv, 
        x="Score", 
        nbins=10, 
        title="Distribution des Scores",
        labels={'Score': 'Score'}
    )
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig)

with open('style.css') as f:
    css = f.read()

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
