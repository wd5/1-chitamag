$(function() {
    if ($('#id_category'))
        {
            LoadFeatureNames($('#id_category').val())
        }

    $('#id_category').live('change', function() {
        LoadFeatureNames($(this).val())
    });

});


function LoadFeatureNames(id)
{
    var select_set = $('.feature_name select')
    $.ajax({
        url: "/load_features_names/",
        data: {
            id_category:id
        },
        type: "POST",
        success: function(data) {
            var id_option = ''
            for (var i = 0; i <= select_set.length-1; i++)
                {
                    if (select_set.eq(i).find('option:selected').val()!='')
                        {   // если объект уже был выделен - то оставляем выделение
                            id_option=select_set.eq(i).find('option:selected').val()
                            select_set.eq(i).html(data)
                            select_set.eq(i).find('option[value="'+id_option+'"]').attr('selected','selected')
                        }
                    else
                        {
                            select_set.eq(i).html(data)
                        }
                }
        },
        error:function(jqXHR,textStatus,errorThrown) {
            $('.feature_name select').html('<option value="" selected="selected">---------</option>');
        }
    });
}
