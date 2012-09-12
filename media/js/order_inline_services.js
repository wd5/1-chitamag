jQuery.expr[':'].regex = function(elem, index, match) {
    var matchParams = match[3].split(','),
        validLabels = /^(data|css):/,
        attr = {
            method: matchParams[0].match(validLabels) ?
                        matchParams[0].split(':')[0] : 'attr',
            property: matchParams.shift().replace(validLabels,'')
        },
        regexFlags = 'ig',
        regex = new RegExp(matchParams.join('').replace(/^\s+|\s+$/g,''), regexFlags);
    return regex.test(jQuery(elem)[attr.method](attr.property));
}

$(function(){
    var order_product_set = $('input[type="hidden"]:regex(name, .*orderproduct_set-[0-9]-id.*)');
    var ids = [];
    for (var i=0; i<=order_product_set.length-1;i++){
        ids.push(order_product_set.eq(i).val());
        ids.push(order_product_set.eq(i).val());
    }
    ids = ids.join(',');
    var divs = false;
    $.ajax({
        url: "/load_serv_rows/",
        data: {
            ids:ids
        },
        type: "POST",
        success: function(data) {
            $('#container').after('<div style="display: none;" class="system_info">'+data+'</div>');
            divs = $('div.tr');
            for (var i=0; i<=order_product_set.length-1;i++){
                var parent = order_product_set.eq(i).parents('tr');
                for (var j=0; j<=divs.length-1;j++){
                    if (divs.eq(j).attr('title')==order_product_set.eq(i).val()){
                        parent.after('<tr><td class="service_td" colspan="5"><div>'+divs[j].innerHTML+'</div></td></tr>');
                    }
                }
            }
            $('div.system_info').remove();
        }
    });

});