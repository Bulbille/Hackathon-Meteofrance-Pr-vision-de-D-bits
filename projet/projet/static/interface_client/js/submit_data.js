$(document).ready(function(){
    $('#myForm').submit(function(e){
        e.preventDefault(); // Empêche le formulaire de se soumettre normalement

        var formData = $(this).serialize(); // Sérialiser les données du formulaire

        $.ajax({
            type: 'POST',
            url: '{% url "submit_data" %}', // URL de la vue de soumission des données
            data: formData,
            success: function(response){
                console.log(response);
                alert("Données soumises avec succès !");
            },
            error: function(xhr, status, error){
                console.error(error);
                alert("Une erreur s'est produite lors de la soumission des données.");
            }
        });
    });
});