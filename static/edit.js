function save_changes() {
    let summary = $("#summary").val();
    let description = $("#description").val();
    let link = $("#link").val();
    let featured = $("#featured").is(':checked');
    let name = $("#name").val();
    $.ajax({
        url: '.',
        type: 'POST',
        data: {
            summary, description, link, name, featured
        },
    }).done(function () {
        let el = document.createElement("p");
        el.className = "popup";
        el.appendChild(document.createTextNode('Data saved successfully'));
        document.body.appendChild(el)
    })
}