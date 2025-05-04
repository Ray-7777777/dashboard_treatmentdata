import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.backends.backend_pdf import PdfPages
import io
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

class DentalTreatmentDashboard:
    def __init__(self, data_path):
        self.df = self._load_data(data_path)
        self._prepare_data()
        
    def _load_data(self, path):
        """Charge les données depuis le fichier CSV"""
        return pd.read_csv(path, sep=";")
    
    def _prepare_data(self):
        """Prétraitement des données"""
        # Conversion des durées en minutes
        self.df['SetupDuration(min)'] = self.df['SetupDuration(sec)'] / 60
        self.df['TreatmentDuration(min)'] = self.df['TreatmentDuration(sec)'] / 60
        self.df['TotalDuration(min)'] = (self.df['SetupDuration(sec)'] + self.df['TreatmentDuration(sec)']) / 60
    
    def _show_kpis(self):
        """Affiche les indicateurs clés de performance"""
        cols = st.columns(5)
        metrics = [
            ("Traitements", len(self.df)),
            ("Durée moyenne", f"{self.df['TotalDuration(min)'].mean():.1f} min"),
            ("Taux d'interruption", f"{100 * (self.df['Interruptions'] > 0).mean():.1f}%"),
            ("Satisfaction patient moyenne", f"{self.df['PatientRating'].mean():.1f}/5"),
            ("Satisfaction docteur moyenne", f"{self.df['DoctorRating'].mean():.1f}/5")
        ]
        
        for col, (label, value) in zip(cols, metrics):
            col.metric(label, value)
    
    def _show_raw_data(self):
        """Affiche les données brutes avec option de téléchargement"""
        st.header("Données Brutes")
        st.dataframe(self.df, height=600, use_container_width=True)
        
        csv = self.df.to_csv(index=False, sep=";").encode('utf-8')
        st.download_button(
            label="Télécharger les données",
            data=csv,
            file_name="donnees_traitements_dentaires.csv",
            mime="text/csv"
        )
    
    def _create_rating_distribution_plot(self):
        """Crée le graphique de distribution des notes avec couleurs"""
        return px.histogram(
            self.df,
            x=['PatientRating', 'DoctorRating'],
            barmode='group',
            title="Distribution des notes patient et docteur",
            labels={'value': 'Note', 'variable': 'Type'},
            color_discrete_sequence=['#636EFA', '#EF553B']
        )
    
    def _create_correlation_heatmap(self):
        """Crée une nouvelle version améliorée de la heatmap de corrélation"""
        corr_matrix = self.df[['NumberOfTeeth', 'SetupDuration(min)', 
                             'TreatmentDuration(min)', 'Interruptions',
                             'Errors', 'PatientRating', 'DoctorRating']].corr()
        
        # Création de la figure matplotlib
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap='coolwarm',
            center=0,
            linewidths=0.5,
            linecolor='white',
            square=True,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        
        # Personnalisation
        ax.set_title("Matrice de Corrélation", pad=20, fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        return fig
    
    def _create_duration_histogram(self):
        """Crée l'histogramme des durées avec couleur"""
        return px.histogram(
            self.df, 
            x='TotalDuration(min)',
            nbins=30,
            title="Distribution des Durées Totales",
            labels={'TotalDuration(min)':'Durée (min)', 'count':'Nombre'},
            marginal='box',
            color_discrete_sequence=['#00CC96']
        )
    
    def _create_teeth_duration_scatter(self):
        """Crée le scatter plot durée vs nombre de dents avec couleur"""
        return px.scatter(
            self.df,
            x='NumberOfTeeth',
            y='TreatmentDuration(min)',
            trendline="lowess",
            title="Durée vs Nombre de dents",
            labels={'NumberOfTeeth': 'Dents', 'TreatmentDuration(min)': 'Durée (min)'},
            color_discrete_sequence=['#AB63FA']
        )
    
    def _create_duration_comparison_boxplot(self):
        """Crée le boxplot de comparaison des durées avec couleurs"""
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=self.df['SetupDuration(min)'], 
            name='Setup',
            marker_color='#636EFA'
        ))
        fig.add_trace(go.Box(
            y=self.df['TreatmentDuration(min)'], 
            name='Traitement',
            marker_color='#EF553B'
        ))
        fig.update_layout(
            title="Comparaison des durées (min)",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def _create_interruptions_histogram(self):
        """Crée l'histogramme des interruptions avec couleur"""
        return px.histogram(
            self.df,
            x='Interruptions',
            title="Interruptions",
            labels={'Interruptions': "Nombre"},
            color_discrete_sequence=['#FFA15A']
        )
    
    def _create_impact_scatter(self, x_col, y_col, title, color):
        """Crée un scatter plot d'impact générique"""
        return px.scatter(
            self.df,
            x=x_col,
            y=y_col,
            trendline="lowess",
            title=title,
            labels={x_col: x_col.replace('_', ' '), y_col: y_col.replace('_', ' ')},
            color_discrete_sequence=[color]
        )
    
    def _create_impact_boxplot(self, x_col, y_col, title, color):
        """Crée un boxplot d'impact générique"""
        return px.box(
            self.df,
            x=x_col,
            y=y_col,
            title=title,
            labels={x_col: x_col.replace('_', ' '), y_col: y_col.replace('_', ' ')},
            color_discrete_sequence=[color]
        )
    
    def _create_errors_histogram(self):
        """Crée l'histogramme des erreurs avec couleur"""
        return px.histogram(
            self.df,
            x='Errors',
            title="Erreurs",
            color_discrete_sequence=['#FF6692']
        )
    
    def _create_duration_patient_scatter(self):
        """Crée le scatter plot durée vs satisfaction patient avec couleur"""
        return px.scatter(
            self.df,
            x='TotalDuration(min)',
            y='PatientRating',
            trendline="lowess",
            title="Durée vs Satisfaction patient",
            color_discrete_sequence=['#636EFA']
        )
    
    def _create_duration_doctor_scatter(self):
        """Crée le scatter plot durée vs satisfaction docteur avec couleur"""
        return px.scatter(
            self.df,
            x='TotalDuration(min)',
            y='DoctorRating',
            trendline="lowess",
            title="Durée vs Satisfaction docteur",
            color_discrete_sequence=['#EF553B']
        )
    
    def _create_rating_correlation_scatter(self):
        """Crée le scatter plot corrélation patient/docteur avec couleur"""
        return px.scatter(
            self.df,
            x='PatientRating',
            y='DoctorRating',
            trendline="ols",
            title="Corrélation patient/docteur",
            color_discrete_sequence=['#00CC96']
        )
    
    def _show_overview(self):
        """Affiche la vue d'ensemble des données"""
        st.header("Vue d'ensemble")
        
        with st.container():
            fig = self._create_rating_distribution_plot()
            st.plotly_chart(fig, use_container_width=True)
            
            st.header("Matrice de Corrélation")
            fig = self._create_correlation_heatmap()
            st.pyplot(fig)
            plt.close()
    
    def _show_time_analysis(self):
        """Analyse des aspects temporels"""
        st.header("Analyse Temporelle")
        
        with st.container():
            fig = self._create_duration_histogram()
            st.plotly_chart(fig, use_container_width=True)
            
            fig = self._create_teeth_duration_scatter()
            st.plotly_chart(fig, use_container_width=True)
            
            fig = self._create_duration_comparison_boxplot()
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_problems_analysis(self):
        """Analyse des problèmes et interruptions - Version graphique par graphique"""
        st.header("Analyse des Problèmes et Erreurs")
        
        # Onglets pour chaque type de visualisation
        tab1, tab2, tab3, tab4 = st.tabs([
            "Distributions", 
            "Impact Durée", 
            "Impact Satisfaction", 
            "Relations"
        ])
        
        with tab1:
            st.subheader("Distribution des problèmes")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Interruptions**")
                fig = self._create_interruptions_histogram()
                st.plotly_chart(fig, use_container_width=True)
                
                stats = self.df['Interruptions'].describe()
                st.markdown(f"""
                - Moyenne: {stats['mean']:.1f}
                - Max: {stats['max']}
                - 75% des cas: ≤ {stats['75%']}
                """)
            
            with col2:
                st.markdown("**Erreurs**")
                fig = px.histogram(
                    self.df,
                    x='Errors',
                    title="Distribution des erreurs",
                    color_discrete_sequence=['#FF6692'],
                    labels={'Errors': 'Nombre d\'erreurs'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                stats = self.df['Errors'].describe()
                st.markdown(f"""
                - Moyenne: {stats['mean']:.1f}
                - Max: {stats['max']}
                - 75% des cas: ≤ {stats['75%']}
                """)
        
        with tab2:
            st.subheader("Impact sur les durées")
            option = st.radio("Type de problème:", 
                            ["Interruptions", "Errors"],
                            horizontal=True)
            
            if option == "Interruptions":
                fig = self._create_impact_scatter(
                    x_col="Interruptions",
                    y_col="TotalDuration(min)",
                    title="Impact des interruptions sur la durée totale",
                    color='#19D3F3'
                )
            else:
                fig = self._create_impact_scatter(
                    x_col="Errors",
                    y_col="TotalDuration(min)",
                    title="Impact des erreurs sur la durée totale",
                    color='#B6E880'
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calcul de corrélation
            corr = self.df[option].corr(self.df['TotalDuration(min)'])
            st.metric("Corrélation avec la durée", f"{corr:.2f}",
                    help="Corrélation de Pearson (0 = pas de lien, 1 = lien fort)")
        
        with tab3:
            st.subheader("Impact sur la satisfaction")
            col1, col2 = st.columns(2)
            
            with col1:
                problem_type = st.selectbox(
                    "Type de problème:",
                    ["Interruptions", "Errors"],
                    key="prob_satisfaction"
                )
            
            with col2:
                rating_type = st.selectbox(
                    "Type de satisfaction:",
                    ["Patient", "Docteur"],
                    key="rating_type"
                )
            
            y_col = "PatientRating" if rating_type == "Patient" else "DoctorRating"
            
            fig = self._create_impact_boxplot(
                x_col=problem_type,
                y_col=y_col,
                title=f"Impact des {problem_type.lower()} sur la satisfaction {rating_type.lower()}",
                color='#FFA15A' if problem_type == "Interruptions" else '#FF6692'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Calcul de corrélation
            corr = self.df[problem_type].corr(self.df[y_col])
            st.metric("Corrélation", f"{corr:.2f}",
                    help="Valeur négative = impact négatif sur la satisfaction")
        
        with tab4:
            st.subheader("Relations entre problèmes")
            fig = px.scatter(
                self.df,
                x='Interruptions',
                y='Errors',
                color='TotalDuration(min)',
                title="Relation entre interruptions et erreurs",
                labels={
                    'Interruptions': 'Interruptions',
                    'Errors': 'Erreurs',
                    'TotalDuration(min)': 'Durée (min)'
                },
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Analyse:**
            - Les points rouges (durées longues) montrent les cas problématiques
            - Relation visible entre nombre d'interruptions et erreurs
            """)
        
    def _show_satisfaction_analysis(self):
        """Analyse de la satisfaction"""
        st.header("Analyse de Satisfaction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = self._create_duration_patient_scatter()
            st.plotly_chart(fig, use_container_width=True)
            
            fig = self._create_duration_doctor_scatter()
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = self._create_rating_correlation_scatter()
            st.plotly_chart(fig, use_container_width=True)
    
    def _add_plot_to_pdf(self, pdf, fig, title=None, is_matplotlib=False):
        """Ajoute un graphique au PDF"""
        if is_matplotlib:
            # Pour les figures matplotlib
            if title:
                fig.suptitle(title, y=1.02, fontsize=14, fontweight='bold')
            pdf.savefig(fig, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            # Pour les figures Plotly
            if title:
                fig.update_layout(title_text=title, title_x=0.5)
            
            img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
            img = Image.open(io.BytesIO(img_bytes))
            
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.axis('off')
            
            if title:
                plt.suptitle(title, y=0.95, fontsize=14, fontweight='bold')
            
            pdf.savefig(bbox_inches='tight', dpi=300)
            plt.close()
    
    def _generate_pdf_report(self):
        """Génère un rapport PDF avec les mêmes graphiques que le dashboard"""
        pdf_buffer = io.BytesIO()
        
        with PdfPages(pdf_buffer) as pdf:
            # Page de titre
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.axis('off')
            title_text = "Rapport des Traitements Dentaires\n\n"
            kpi_text = "\n".join([
                f"• Nombre de traitements: {len(self.df)}",
                f"• Durée moyenne: {self.df['TotalDuration(min)'].mean():.1f} min",
                f"• Taux d'interruption: {100 * (self.df['Interruptions'] > 0).mean():.1f}%",
                f"• Satisfaction patient moyenne: {self.df['PatientRating'].mean():.1f}/5",
                f"• Satisfaction docteur moyenne: {self.df['DoctorRating'].mean():.1f}/5"
            ])
            ax.text(0.1, 0.7, title_text, fontsize=18, fontweight='bold')
            ax.text(0.1, 0.3, kpi_text, fontsize=14)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
            
            # Vue d'ensemble
            self._add_plot_to_pdf(pdf, self._create_rating_distribution_plot(), "Distribution des notes")
            self._add_plot_to_pdf(pdf, self._create_correlation_heatmap(), "Matrice de Corrélation", is_matplotlib=True)
            
            # Analyse Temporelle
            self._add_plot_to_pdf(pdf, self._create_duration_histogram(), "Distribution des Durées")
            self._add_plot_to_pdf(pdf, self._create_teeth_duration_scatter(), "Durée vs Nombre de dents")
            self._add_plot_to_pdf(pdf, self._create_duration_comparison_boxplot(), "Comparaison des durées")
            
            # Analyse des Problèmes (version par défaut)
            self._add_plot_to_pdf(pdf, self._create_interruptions_histogram(), "Distribution des interruptions")
            self._add_plot_to_pdf(pdf, 
                self._create_impact_scatter("Interruptions", "TotalDuration(min)", "Impact des interruptions sur la durée", '#19D3F3'),
                "Impact des interruptions sur la durée"
            )
            self._add_plot_to_pdf(pdf, self._create_errors_histogram(), "Distribution des erreurs")
            self._add_plot_to_pdf(pdf,
                self._create_impact_boxplot("Errors", "PatientRating", "Impact des erreurs sur la satisfaction patient", '#B6E880'),
                "Impact des erreurs sur la satisfaction"
            )
            
            # Analyse de Satisfaction
            self._add_plot_to_pdf(pdf, self._create_duration_patient_scatter(), "Durée vs Satisfaction patient")
            self._add_plot_to_pdf(pdf, self._create_duration_doctor_scatter(), "Durée vs Satisfaction docteur")
            self._add_plot_to_pdf(pdf, self._create_rating_correlation_scatter(), "Corrélation patient/docteur")
            
        return pdf_buffer
    
    def run(self):
        """Lance l'application dashboard"""
        # Configuration de la page
        st.set_page_config(
            page_title="Dashboard Traitements Dentaires", 
            layout="wide",
            page_icon="🦷"
        )
        st.title("Dashboard des Traitements Dentaires")
        
        # Affichage des KPIs
        self._show_kpis()
        
        # Onglets principaux
        tabs = st.tabs([
            "Vue d'ensemble", 
            "Analyse Temporelle", 
            "Problèmes", 
            "Satisfaction",
            "Données Brutes"
        ])
        
        with tabs[0]:
            self._show_overview()
        with tabs[1]:
            self._show_time_analysis()
        with tabs[2]:
            self._show_problems_analysis()
        with tabs[3]:
            self._show_satisfaction_analysis()
        with tabs[4]:
            self._show_raw_data()
        
        # Export PDF dans la sidebar
        st.sidebar.header("Export")
        if st.sidebar.button("📄 Générer PDF"):
            with st.spinner("Génération du rapport PDF..."):
                pdf_buffer = self._generate_pdf_report()
                st.sidebar.success("Rapport généré!")
                st.sidebar.download_button(
                    label="Télécharger PDF",
                    data=pdf_buffer.getvalue(),
                    file_name="rapport_traitements_dentaires.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    dashboard = DentalTreatmentDashboard("DataScienceTreatmentData.csv")
    dashboard.run()