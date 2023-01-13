function registration(){
    token = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajax({
        type: 'POST',
        url: '/registrar/',
        data: {
            csrfmiddlewaretoken: token
        },
        success: function(result){
            console.log('foi')
            $("#ajax-message").text('Executado!');
        }
    });
}