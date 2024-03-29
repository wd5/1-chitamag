$(function(){

    $('.filter_brands li').live('click',function(){
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');
        var mfr_id = $(this).find('a').attr('name')
        var exist = false
        var curr_send_link = $('a.filter_submit_btn').attr('href')
        if (curr_send_link=='#')
            {$('a.filter_submit_btn').attr('href','?mfr='+mfr_id)}
        else
            {
                var get_param_array = curr_send_link.split('&');
                var length = get_param_array.length
                for (var i = 0; i <= length-1; i++)
                    {
                        part = get_param_array[i].split('=')
                        if (part[0].substring(0, 1) == "?")
                            {
                                part[0] = part[0].substring(1)
                            }
                        if (part[0]=='mfr')
                            {
                                exist = true
                                part[1]=mfr_id
                            }
                        get_param_array[i] = part.join('=')
                    }

                if (!exist)
                    {get_param_array.push('mfr='+mfr_id);}

                curr_send_link = get_param_array.join('&')
                if (curr_send_link != "?")
                    {
                        curr_send_link = '?' + curr_send_link
                    }
                $('a.filter_submit_btn').attr('href',curr_send_link)
            }

        return false;
    });

    $('.filter_params li').live('click',function(){
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');
        var feature_value = $(this).find('a').html()
        var feature_id = $(this).parent().attr('name')
        var str_value = feature_id+'^'+feature_value
        var exist = false
        var curr_send_link = $('a.filter_submit_btn').attr('href')
        if (curr_send_link=='#')
            {$('a.filter_submit_btn').attr('href','?features='+str_value)}
        else
            {
                var get_param_array = curr_send_link.split('&');
                var length = get_param_array.length
                for (var i = 0; i <= length-1; i++)
                    {
                        part = get_param_array[i].split('=')
                        if (part[0].substring(0, 1) == "?")
                            {
                            part[0] = part[0].substring(1)
                            }
                        if (part[0]=='features')
                            {
                            exist = true
                            var feature_array = part[1].split('|');
                            var length_fa = feature_array.length
                            var exist_f = false
                            for (var k = 0; k <= length_fa-1; k++)
                                {
                                feature = feature_array[k].split('^')
                                if (feature[0] == feature_id)
                                    {
                                    exist_f = true
                                    feature[1] = feature_value
                                    }
                                feature_array[k] = feature.join('^')
                                }
                            if (exist_f==false)
                                {
                                feature_array.push(str_value)
                                }
                            part[1] = feature_array.join('|')
                            }
                        get_param_array[i] = part.join('=')
                    }

                if (!exist)
                    {get_param_array.push('features='+str_value);}

                curr_send_link = get_param_array.join('&')
                if (curr_send_link != "?")
                    {
                    curr_send_link = '?' + curr_send_link
                    }
                $('a.filter_submit_btn').attr('href',curr_send_link)
            }

        return false;
    });

    $('.item_views_menu li').live('click',function(){
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');
        if ($(this).find('a').html()=='Фотогалерея')
            {
            $('.item_page_l .item_gal').show();
            $('.item_page_l .params').hide();}
        else
            {
            $('.item_page_l .item_gal').hide();
            $('.item_page_l .params').show();}
        return false;
    });

    $('.all_params_lnk a').live('click',function(){
        $('.item_views_menu li').click()
        return false;
    });

    $('.fancybox').fancybox();

    $('#oneclick_submit').live('click',function(){
            $.ajax({
                url: "/check_oneclick_form/",
                data: {
                    phone:$('#id_phone').val(),
                    product:$('#id_product').val(),
                    product_description:$('#id_product_description').val(),
                    product_price:$('#id_product_price').val()
                },
                type: "POST",
                success: function(data) {
                    if (data=='success')
                        {$('.oneclick_form').replaceWith("<div style='height: 150px;text-align: center;padding-top: 75px;'>Благодарим за заказ! В ближайшее время с вами свяжутся.</div>");}
                    else{
                        $('.oneclick_form').replaceWith(data);
                    }
                }
            });
            return false;
        });

    $('.item_gal li').live('click',function(){
        var el = $(this)
        var link = el.find('div.replace_img a').clone()
        var rel = $('.item_gal_zl a').attr('rel')
        el.parent().find('a').attr('rel',rel)
        el.find('div.replace_img a').removeAttr('rel')
        el.parent().find('li').removeClass('curr');
        el.toggleClass('curr');
        link.attr('rel',rel)
        $('.item_gal_zl a').replaceWith(link)
        $('.item_gal_zl').append('<script type="text/javascript">$(".fancybox").fancybox()</script>')
        return false;
    });




    $('.order_menu li').live('click',function(){
        var curr_class = $(this).find('a').attr('class');
        $(this).parent().find('li').removeClass('curr');
        $(this).toggleClass('curr');

        $('#id_order_carting [value="'+curr_class+'"]').attr('selected','selected')


        $('.contact_info').hide();
        $('div.'+curr_class).show();
        return false;
    });

    $('.load_items').live('click',function(){

        var el = $(this);
        var parent = $(this).parents('.load_block');
        var tr_count = parent.find('table tr').length;
        $.ajax({
            url: "/load_items/",
            data: {
                load_ids: parent.find('#loaded_ids').val(),
                m_name: parent.find('#m_name').val(),
                a_name: parent.find('#a_name').val(),
                tr_count: tr_count
            },
            type: "POST",
            success: function(data) {
                parent.find('tbody').append(data)
                parent.find('.loaded:eq(0)').fadeIn("fast", function (){ //появление по очереди
                        $(this).next().fadeIn("fast", arguments.callee);
                    });
                //parent.find('.loaded').fadeIn('slow')  //простое появление
                parent.find('#loaded_ids').val(parent.find('#new_load_ids').val())
                parent.find('tr').removeClass('loaded')
                var rctxt = parent.find('#remaining_count_text').val()
                var rc = parent.find('#remaining_count').val()
                if (rctxt!=undefined)
                    {el.html(rctxt)}
                if (rc<=0)
                    {parent.find('.more').remove()}
                parent.find('#remaining_count_text').remove()
                parent.find('#new_load_ids').remove()
                parent.find('#remaining_count').remove()

            }
        });

        return false;
    });


    // слайдер на главной

    function SlideToLeft()
    {
        var curr_slide = $('li.curr_slide')
        if (curr_slide.prev().html())
            {
                curr_slide.toggleClass('curr_slide');
                curr_slide.prev().toggleClass('curr_slide');
            }
        else
            {
                curr_slide.toggleClass('curr_slide');
                curr_slide.parent().children().last().toggleClass('curr_slide');
            }
    }

    function SlideToRight()
    {
        var curr_slide = $('li.curr_slide')
        if (curr_slide.next().html())
            {
                curr_slide.toggleClass('curr_slide');
                curr_slide.next().toggleClass('curr_slide');
            }
        else
            {
                curr_slide.toggleClass('curr_slide');
                curr_slide.parent().children().first().toggleClass('curr_slide');
            }
    }

    var myTimer = 0

    function SlidePromos(){
       clearInterval(myTimer);
       myTimer = setInterval( function(){SlideToRight();} , 7000);
       myTimer;
    }

    SlidePromos();

    $('a.promo_arr_l').live('click',function(){
        SlideToLeft();
        SlidePromos();
        return false;
    });

    $('a.promo_arr_r').live('click',function(){
        SlideToRight();
        SlidePromos();
        return false;
    });




    //Анимация корзины при изменении
    function animate_cart(){

        $('.cartbox').animate({
                opacity: 0.25
            }, 200, function() {
                $(this).animate({
                    opacity: 1
                },200);
            }
        );

    }

    function create_img_fly(el)
    {
        var img = el.html();
        var offset = el.find('img').offset();
        element = "<div class='img_fly'>"+img+"</div>";
        $('body').append(element);
        $('.img_fly').css({
            'position': "absolute",
            'z-index': "1000",
            'left': offset.left,
            'top': offset.top
        });

    }

    //Добавление товара в корзину

    $('.buy_btn').live('click',function(){
        var product_id = $(this).attr('name')
        var parent_blk = $(this).parents('.item_page')

        if (product_id){
            $.ajax({
                type:'post',
                url:'/add_product_to_cart/',
                data:{
                    'product_id':product_id
                },
                success:function(data){
                    $('.img_fly').remove();
                    create_img_fly(parent_blk.find('.product_img'));

                    $('.cartbox').replaceWith(data);

                    var fly = $('.img_fly');
                    var left_end = $('.cartbox').offset().left;
                    var top_end = $('.cartbox').offset().top;

                    fly.animate(
                        {
                            left: left_end,
                            top: top_end
                        },
                        {
                            queue: false,
                            duration: 600,
                            easing: "swing"
                        }
                    ).fadeOut(600);

                    setTimeout(function(){
                        animate_cart();
                    } ,600);

                },
                error:function(jqXHR,textStatus,errorThrown){

                }
            });
        }

    });




    $('.cart_option').hover(
        function() {
            $(this).find('.cart_option_qty ul').show();
        },
        function() {
            $(this).find('.cart_option_qty ul').hide();
        }
    );

    $('.cart_option_name').live('click',function(){
        var parent = $(this).parent()
        var cart_product_id = $(this).parents('div.cart_item').find('.cart_item_id').val()
        var list = parent.find('.cart_option_qty ul')
        var curr_count = parent.find('.service_count')
        parent.toggleClass('cart_option_checked');
        if (list.html() != '')
            {
            if (parent.is('.cart_option_checked'))
                {
                if (list.find('li[class="curr"] a').html())
                    {}
                else
                    {list.find('li').first().addClass('curr');
                    curr_count.val('1')
                    }
                }
            else
                {list.find('li').removeClass('curr');}
            }

        $.ajax({
            type:'post',
            url:'/change_cart_product_service/',
            data:{
                'cart_product_id':cart_product_id,
                'serv_id':parent.find('.id_serv').val(),
                'serv_count':parent.find('.cart_option_qty li[class="curr"] a').attr('name'),
                'not_delete':parent.is('.cart_option_checked')
            },
            success:function(data){
                data = eval('(' + data + ')');
                $('.cart_total .cart_price_val').html(data.cart_str_total);
                if (data.cart_str_total=='0')
                    {$('.cart_submit_btn').attr('disabled', true);}
                else
                    {$('.cart_submit_btn').attr('disabled', false);}
                parent.find('.cart_price_val').html(data.serv_str_total);
            },
            error:function(data){
            }
        });
    });

    $('div.cart_option_qty a.dot').live('click',function(){
        var parent = $(this).parents('div.cart_option')
        var is_checked = parent.is('.cart_option_checked')
        var cart_product_id = $(this).parents('div.cart_item').find('.cart_item_id').val()
        var curr_count = parent.find('.service_count')
        var el = $(this)
        var count = $(this).parents('ul').find('li[class="curr"] a').attr('name')
        el.parents('ul').find('li').removeClass('curr');
        el.parent().toggleClass('curr');
        curr_count.val(el.attr('name'))
        if (!is_checked)
            {parent.find('.cart_option_name').click();}
        else
            {//меняем количество услуги
                $.ajax({
                    type:'post',
                    url:'/change_cart_product_service_count/',
                    data:{
                        'cart_product_id':cart_product_id,
                        'serv_id':parent.find('.id_serv').val(),
                        'serv_count':parent.find('.cart_option_qty li[class="curr"] a').attr('name')
                    },
                    success:function(data){
                        data = eval('(' + data + ')');
                        $('.cart_total .cart_price_val').html(data.cart_str_total);
                        if (data.cart_str_total=='0')
                            {$('.cart_submit_btn').attr('disabled', true);}
                        else
                            {$('.cart_submit_btn').attr('disabled', false);}
                        parent.find('.cart_price_val').html(data.serv_str_total);
                    },
                    error:function(data){
                    }
                });
            }
        return false;
    });

    $('.cart_qty_btn').live('click',function(){
        $('.cart_qty_btn').attr('disabled', true);
        $(this).attr('disabled', false);
        $(this).parents('.cart_qty').find('.cart_qty_modal').show();
        $(this).find('.cart_qty_modal_ok').attr('disabled', false);
        $('.cart_submit_btn').attr('disabled', true);
        $('.cart_back').attr('disabled', true);
        $('.delete_cart_id').attr('disabled', true);
    });

    $('.cart_qty_modal_text').live('keypress',function(e){
        if(e.which == 13)
            $('.cart_qty_modal_ok').trigger("click");
        else
        if( e.which!=8 && e.which!=0 && (e.which<48 || e.which>57))
        {
            alert("Только цифры");
            return false;
        }
    });

    //Подсчёт стоимости
    $('.cart_qty_modal_text').live('keyup',function(){
        var el = $(this)
        var count = el.val();
        if (count){
            count = parseInt(count);
            if (count==0){
                $('.cart_qty_modal_text').val('1');
                count = 1;
            }
            if (count > 999){
                $('.cart_qty_modal_text').val('999');
                count = 999;
            }

            var product_price = el.parent().find('.cart_qty_price span').html();

            product_price = parseFloat(product_price);
            var sum = product_price*count;
            if ((sum % 1)==0){
                sum = sum.toFixed(0);
            }
            else{
                sum = sum.toFixed(2);
            }
            el.parent().find('.cart_qty_total_price span').text(sum);
        }
    });

        //Кнопка Созранить в изменении количества в корзине
    $('.cart_qty_modal_ok').live('click', function(){
        var el = $(this);
        var parent = el.parents('.cart_qty_modal');
        var cart_item = el.parents('.cart_item');
        var uls_list = cart_item.find('.cart_option .cart_option_qty ul');
        var initial_count = parent.find('.initial_count').val();
        var new_count = parent.find('.cart_qty_modal_text').val();
        var cart_product_id = parent.find('.cart_qty_item_id').val();

        if (new_count && cart_product_id && initial_count){
            if (new_count != initial_count){
                $.ajax({
                    type:'post',
                    url:'/change_cart_product_count/',
                    data:{
                        'cart_product_id':cart_product_id,
                        'new_count':new_count
                    },
                    success:function(data){
                        data = eval('(' + data + ')');
                        cart_item.find('.cart_des>.cart_price>.cart_price_val').html(data.tr_str_total);
                        cart_item.find('.cart_qty_btn').val(new_count);
                        parent.find('.initial_count').val(new_count);
                        parent.find('.cart_qty_modal_text').val(new_count);
                        parent.find('.cart_qty_total_price span').text(data.tr_str_total);
                        $('.cart_total .cart_price_val').html(data.cart_str_total);
                        if (data.cart_str_total=='0')
                            {$('.cart_submit_btn').attr('disabled', true);}
                        else
                            {$('.cart_submit_btn').attr('disabled', false);}
                        $('.cart_submit').attr('disabled', false);
                        $('.cart_qty_btn').attr('disabled', false);
                        $('.cart_item_restore_btn').attr('disabled', false);
                        parent.hide();
                    },
                    error:function(data){
                        $('.cart_submit_btn').attr('disabled', false);
                        $('.cart_qty_btn').attr('disabled', false);
                        $('.cart_item_restore_btn').attr('disabled', false);
                    }
                });

                    var length_ulL = uls_list.length
                    var str = ''
                    if (new_count>10)
                        {new_count=10}
                    for (var i = 1; i <= new_count; i++)
                        {str += '<li><a class="dot" href="#" name="' + i + '">' + i + '</a></li>'}
                    for (var k = 0; k <= length_ulL-1; k++)
                            {
                            var ul = uls_list.eq(k)
                            var curr_count = ul.parents('.cart_option').find('.service_count').val()

                            if ((new_count>initial_count) && (new_count>1))
                                {
                                if (!curr_count)
                                    {
                                        ul.html(str)
                                    }
                                else
                                    {
                                        ul.html(str)
                                        if (ul.parents('div.cart_option').is('.cart_option_checked'))
                                            {ul.find('a[name="' + curr_count + '"]').parent().addClass('curr')}
                                    }
                                }
                            if ((new_count<initial_count) && (new_count>1))
                                {
                                    if (!curr_count)
                                        {
                                            ul.html(str)
                                        }
                                    else
                                        {
                                            ul.html(str)
                                            if (curr_count>new_count)
                                                {
                                                if (ul.parents('div.cart_option').is('.cart_option_checked'))
                                                    {var dot = ul.find('a[name="' + new_count + '"]')
                                                    dot.parent().addClass('curr')
                                                    dot.click()}

                                                }
                                            else
                                                {if (ul.parents('div.cart_option').is('.cart_option_checked'))
                                                    {ul.find('a[name="' + curr_count + '"]').parent().addClass('curr')}}
                                        }
                                }
                            if (new_count==1)
                                {
                                    ul.html(str)
                                    if (ul.parents('div.cart_option').is('.cart_option_checked'))
                                        {var dot = ul.find('a[name="' + new_count + '"]')
                                        dot.parent().addClass('curr')
                                        dot.click()}
                                    ul.html('')
                                }
                            }
            }

        }
        $('.cart_submit_btn').attr('disabled', false);
        return false;

    });

    $('.cart_qty_modal_cancel').live('click', function(){
        var el = $(this)
        var parent = el.parents('.cart_qty_modal')
        parent.hide();
        parent.find('.cart_qty_modal_ok').attr('disabled', true);
        $('.cart_submit_btn').attr('disabled', false);
        $('.cart_qty_btn').attr('disabled', false);
        $('.cart_item_restore_btn').attr('disabled', false);
    });

    $('.delete_cart_id').live('click', function(){
        var el = $(this);
        var cart_product_id = el.attr('rel');
        var parent = el.parents('.cart_item');
        if (cart_product_id){
            $.ajax({
                type:'post',
                url:'/delete_product_from_cart/',
                data:{
                    'cart_product_id':cart_product_id
                },
                success:function(data){
                    data = eval('(' + data + ')');
                    $('.cart_total .cart_price_val').html(data.cart_total);
                    if (data.cart_total=='0')
                        {$('.cart_submit_btn').attr('disabled', true);}
                    else
                        {$('.cart_submit_btn').attr('disabled', false);}
                    parent.append('<div class="cart_item_deleted"><a class="cart_back" name="'+data.cart_product_id+'" href="#">Вернуть</a></div>')
                },
                error:function(data){
                }
            });
        }
        return false;
    });

    $('.cart_back').live('click', function(){
        var el = $(this);
        var cart_product_id = el.attr('name');
        var parent = el.parents('.cart_item');
        if (cart_product_id){
            $.ajax({
                type:'post',
                url:'/restore_product_to_cart/',
                data:{
                    'cart_product_id':cart_product_id
                },
                success:function(data){
                    data = eval('(' + data + ')');
                    $('.cart_total .cart_price_val').html(data.cart_total);
                    if (data.cart_total=='0')
                        {$('.cart_submit_btn').attr('disabled', true);}
                    else
                        {$('.cart_submit_btn').attr('disabled', false);}
                    parent.find('.cart_item_deleted').remove()
                },
                error:function(data){
                }
            });
        }
        return false;
    });

});

function SetPriceSlider(min, max, start)
{
    $( "#filter_price_slider" ).slider({
		range: "min",
		value: start,
		min: min,
		max: max,
		slide: function( event, ui ) {
            $(this).parent().find( ".filter_price_input input" ).val( ui.value );
		},
        stop: function( event, ui ) {
            var val = $(this).slider( "option", "value");
            var exist = false;
            var curr_send_link = $('a.filter_submit_btn').attr('href');
            if (curr_send_link=='#')
                {$('a.filter_submit_btn').attr('href','?price_filter='+val)}
            else
                {
                    var get_param_array = curr_send_link.split('&');
                    length = get_param_array.length;
                    for (var i = 0; i <= length-1; i++)
                        {
                            part = get_param_array[i].split('=');
                            if (part[0].substring(0, 1) == "?")
                                {
                                    part[0] = part[0].substring(1)
                                }
                            if (part[0]=='price_filter')
                                {
                                    exist = true
                                    part[1]=val
                                }
                            get_param_array[i] = part.join('=')
                        }
                    if (!exist)
                        {get_param_array.push('price_filter='+val);}
                    var curr_send_link = get_param_array.join('&');
                    if (curr_send_link != "?")
                        {
                            curr_send_link = '?' + curr_send_link
                        }
                    $('a.filter_submit_btn').attr('href',curr_send_link)
                }

        }
	});
	$( ".filter_price_input" ).val( start );
}

function SetShipSlider(min, max, start)
{
    $( "#filter_ship_slider" ).slider({
		range: "min",
		value: start,
		min: min,
		max: max,
		slide: function( event, ui ) {
            $(this).parent().find( ".filter_price_input input" ).val( ui.value );
		},
        stop: function( event, ui ) {
            var val = $(this).slider( "option", "value" );
            var exist = false;
            var curr_send_link = $('a.filter_submit_btn').attr('href');
            $(this).parent().find('.plural_value').html(plural_str(val, 'день','дня','дней'));
            if (curr_send_link=='#')
                {$('a.filter_submit_btn').attr('href','?ship_filter='+val)}
            else
                {
                    var get_param_array = curr_send_link.split('&');
                    length = get_param_array.length
                    for (var i = 0; i <= length-1; i++)
                        {
                            part = get_param_array[i].split('=')
                            if (part[0].substring(0, 1) == "?")
                                {
                                    part[0] = part[0].substring(1)
                                }
                            if (part[0]=='ship_filter')
                                {
                                    exist = true
                                    part[1]=val
                                }
                            get_param_array[i] = part.join('=')
                        }
                    if (!exist)
                        {get_param_array.push('ship_filter='+val);}
                    var curr_send_link = get_param_array.join('&')
                    if (curr_send_link != "?")
                        {
                            curr_send_link = '?' + curr_send_link
                        }
                    $('a.filter_submit_btn').attr('href',curr_send_link)
                }

        }
	});
	$( ".filter_ship_input" ).val( start );
}

function plural_str(i, str1, str2, str3){
    function plural (a){
        if ( a % 10 == 1 && a % 100 != 11 ) return 0
            else if ( a % 10 >= 2 && a % 10 <= 4 && ( a % 100 < 10 || a % 100 >= 20)) return 1
            else return 2;
        }

    switch (plural(i)) {
        case 0: return str1;
        case 1: return str2;
        default: return str3;
    }
}