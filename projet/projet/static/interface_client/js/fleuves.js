$(document).ready(function() {
    // Trie la liste des fleuves par ordre alphabétique
    var options = $('#fleuve option');
    options.detach().sort(function(a, b) {
        var at = $(a).text();
        var bt = $(b).text();
        return at.localeCompare(bt);
    });
    $('#fleuve').append(options);

    // Ajoute un champ de recherche pour filtrer les options des fleuves
    $('#search').on('input', function() {
        var searchText = $(this).val().toLowerCase();
        $('#fleuve option').each(function() {
            var optionText = $(this).text().toLowerCase();
            var isVisible = optionText.indexOf(searchText) !== -1;
            $(this).toggle(isVisible);
        });
    });
});