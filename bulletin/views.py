from django.shortcuts import render, get_object_or_404
from admin_site.models import *
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
# Create your views here.

def send_custom_email(subject, template_name, context, recipient_list):
    """
    Envoie un email personnalisé.

    :param subject: Sujet de l'email
    :param template_name: Nom du fichier de template HTML pour l'email
    :param context: Contexte pour rendre le template
    :param recipient_list: Liste des destinataires de l'email
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = 'prodistributionltd237@gmail.com'
    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )

def index(request):
    """
    Retourne l'élève avec la plus haute moyenne
    """
    eleves = Eleve.objects.select_related('classe', 'user').all()
    
    if not eleves.exists():
        return None
    
    meilleur_eleve = None
    meilleure_moyenne = 0
    
    for eleve in eleves:
        moyenne = eleve.moyenne
        if moyenne > meilleure_moyenne:
            meilleure_moyenne = moyenne
            meilleur_eleve = eleve
    
    """
    Calcule la moyenne générale de toutes les classes
    """
    classes = Classe.objects.all()
    
    if not classes.exists():
        return 0
    
    total_moyennes = Decimal('0')
    nb_classes = 0
    
    for classe in classes:
        moyenne = classe.moyenne_generale
        if moyenne > 0:
            total_moyennes += Decimal(str(moyenne))
            nb_classes += 1
    
    if nb_classes == 0:
        return 0
    
    moyenne_generale= round(float(total_moyennes) / nb_classes, 2)

    """
    Calcule le pourcentage de réussite du lycée
    seuil: note minimale pour considérer qu'un élève a réussi (par défaut 10/20)
    """
    eleves = Eleve.objects.all()
    
    if not eleves.exists():
        return 0
    
    nb_eleves_avec_notes = 0
    nb_eleves_reussis = 0
    
    for eleve in eleves:
        moyenne = eleve.moyenne
        if moyenne > 0:  # Élève ayant au moins une note
            nb_eleves_avec_notes += 1
            if moyenne >= 10:
                nb_eleves_reussis += 1
    
    if nb_eleves_avec_notes == 0:
        return 0
    
    pourcentage = round((nb_eleves_reussis / nb_eleves_avec_notes) * 100, 2)
    
    context = {
        'meilleur_eleve':meilleur_eleve,
        'eleve':Eleve.objects.count(),
        'enseignant':Enseignant.objects.count(),
        'classes':Classe.objects.all(),
        'moyenne_generale':moyenne_generale,
        'pourcentage':pourcentage
    }
    return render(request, 'classes.html', context)

def get_classe_moyenne(request, classe_id):
    # On récupère l'évaluation : (matière + classe + séquence)
    classe = get_object_or_404(Classe, id=classe_id)
    # On récupère tous les élèves de la classe liée à cette évaluation
    eleves = Eleve.objects.filter(classe=classe_id)

    return render(request, "moyenne_eleve.html", {
        "classe": classe,
        "eleves": eleves,
    })

def download_bul_student(request, eleve_id):

    eleve = get_object_or_404(Eleve, id=eleve_id)
    matieres = Matiere.objects.filter(classe=eleve.classe).distinct()
    """
    Retourne toutes les notes de la séquence 1 d'un élève
    """    
    notes = Note.objects.filter(
        eleve=eleve,
        evaluation__type_evaluation="1"
    ).select_related('evaluation__matiere', 'evaluation')
    
    if not notes.exists():
        return {
            'eleve': eleve,
            'sequence': '1',
            'notes': [],
            'total_notes': 0,
            'moyenne_sequence': 0
        }
    
    notes_data = []
    somme_notes_coefficients = 0
    somme_notes = 0
    for note in notes:

        somme_notes += float(note.note)
        somme_notes_coefficients += float(note.evaluation.matiere.coefficient*note.note)
        notes_data.append({
            'mention':note.mention,
            'rang':note.rang,
            'matiere': note.evaluation.matiere,
            'coefficient': note.evaluation.matiere.coefficient,
            'note': float(note.note),
            'note_coeffecient': float(note.evaluation.matiere.coefficient*note.note),
        })
    
    
    # sum_note = sum(item.note for item in notes_data)
    context = {
       'eleve' : eleve,
       'matieres' : matieres,
       'notes': notes_data,
       'somme_notes': somme_notes,
       'somme_notes_coefficients':somme_notes_coefficients,
    }
    template = "mail_parent.html"
    objet = "Lycée bilingue de bojongo"
    send_custom_email(
        objet,
        template,
        context,
        [eleve.email_parent]
    )
    html_string = render_to_string('bulletin.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()


    filename=f'bulletin_{eleve}_{eleve.classe}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response
    # return render(request, 'bulletin.html', context) 