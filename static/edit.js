function save_changes() {
    let summary = $("#summary").val();
    let description = $("#description").text();
    let link = $("#link").val();
    let name = $("#name").val();
    $.ajax({
        url: '.',
        type: 'POST',
        data: {
            summary, description, link, name
        },
    }).done(function () {
        let el = document.createElement("p");
        el.className = "popup";
        el.appendChild(document.createTextNode('Data saved successfully'));
        document.body.appendChild(el)
    })
}