$(document).ready(function() {
    // Trie la liste des villes par ordre alphabétique
    var options = $('#ville option');
    options.detach().sort(function(a, b) {
        var at = $(a).text();
        var bt = $(b).text();
        return (at > bt) ? 1 : ((at < bt) ? -1 : 0);
    });
    $('#ville').append(options);

    // Ajoute un champ de recherche
    $('#search').on('input', function() {
        var searchText = $(this).val().toLowerCase();
        $('#ville option').each(function() {
            var optionText = $(this).text().toLowerCase();
            var isVisible = optionText.indexOf(searchText) !== -1;
            $(this).toggle(isVisible);
        });
    });
});

