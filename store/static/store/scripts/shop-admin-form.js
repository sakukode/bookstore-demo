function getCities(state_id) {
    let $ = django.jQuery;
    $.get('/store/cities/' + state_id, function (resp){
        let cities = '<option value="" selected="">---------</option>'
        $.each(resp.data, function(i, item){
           cities += '<option value="'+ item.id +'">'+ item.name +'</option>'
        });
        $('#id_city').html(cities);
    });
}