/* Copyright (C) 2013  Guilherme Guerra <guerrinha@comum.org>
 * Copyright (C) 2013  Governo do Estado do Rio Grande do Sul
 *
 *   Author: Guilherme Guerra <guilherme-guerra@sgg.rs.gov.br>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

$(window).load(function () {

    $('.carousel').carousel();

    // $('#myCarousel .item').click(function(){
    //     console.log("Clicado");
    // });
    $('#myCarousel .item a').fancybox({
        minWidth: 500,
        minHeight: 300
    });

    $('.toottip').tooltip();

    $('.icon-list').click(function(){
        $('#lista-obras').fadeIn();
    });

    $('.comentar').click(function(){
        $('.comente').fadeIn();
    });

    $(".seguirobra").each(function(){
        var obj = $(this);
        obj.fancybox({
            afterLoad: function(upcoming, current){
                // $('.main-follow').find("input[type=text]").val("");
                $('.main-follow').find(".alert").hide();
            },
            afterShow: function(){
                // $('.main-follow').find('a[target=#follow-email]').trigger('click');
                $('.main-follow').find('a[target='+obj.attr('data-panel')+']').trigger('click');
            }
        });
    });

    var showMsg = function(status, otherclass){
        // alert(status);
        $(".alert").html(status);
        if(otherclass){
            $(".alert").addClass(otherclass);
        }
        $(".alert").show();

    };

    var ret = function(data) {
        var pData = $.parseJSON(data);

        /* It's everything ok, let's get out */
        if (pData.status === 'ok') {
          showMsg('Obrigado por sua contribuição! ','alert-success');
          if(pData.refresh){
            window.setTimeout(function(){
                window.location.reload();
            },1000);
          }
          $('#part-geral').clearFields();
        } else {
          showMsg(pData.message);
        }
    };

    $('#part-geral').ajaxForm({
        beforeSubmit: function(){
            // console.log($('#accept_Tos').is(':checked'));
            if( $('#conteudo').val() == "" || $('#titulo').val() == "" ){
                alert('Você precisa preencher o Título e a Sua Contribuição!')
                $('#titulo').focus();
                return false;
            }

            if(!$('#accept_Tos').is(':checked')){
                alert('Você precisa aceitar os termos de uso!')
                return false;
            }

        },
        success:ret
    });

    var retSeguir = function(data){
        showMsg('Obrigado! Agora você receberá informações sobre esta obra.','alert-success');
        window.setTimeout(function(){
            $.fancybox.close();
        },3000);
    }

    $('#seguirobraform .ajaxform').ajaxForm({
        success:retSeguir,
        beforeSubmit: function (arr, form, options) {
            form.find('input[type=submit]').attr('disabled','disabled');
            form.find('input[type=submit]').removeClass('btn-success');
        }
    });

    $('#seguirobraform a').click(function(){
        // alert('vai abrir ' + this.target );
        $('.main-follow .follow').hide();
        $(this.target).show();
        $(this.target).find('input[type=submit]').removeAttr('disabled');
        $(this.target).find('input[type=submit]').addClass('btn-success');
        $(this.target).find("input[type=text]").focus();
        return false;
    });

    $('.botoesparticipar a').mouseenter( function() {
        $(this).find('.funcao').stop().animate({ opacity: 0, left: "-80px" }, 'slow');
        $(this).find('.help-text').stop().show().animate({ opacity: 100, marginLeft: "50px" }, 'slow');
        $(this).find('.help-text').queue(function () {
            $(this).css('white-space','normal');
            $(this).dequeue();
        });

    }).mouseleave( function() {
        $(this).find('.help-text').css('white-space','nowrap');
        $(this).find('.funcao').stop().animate({ opacity: 100, left: "0px" }, 'slow');
        $(this).find('.help-text').stop().animate({ opacity: 0, marginLeft: "380px" }, 'slow');

    });

    $(".cmore").click(function(){
        if($('.comofunciona').hasClass('fechado')){
            $('.comofunciona').switchClass("fechado","aberto", 600);
            $(this).html('-');
        }else{
            $('.comofunciona').switchClass("aberto","fechado", 600);
            $(this).html('+');
        }
    });

    $('.botoesparticipar a').toggle( function() {
        $('.suplementar').fadeIn();
        $('.updates').hide();
        $('.api-content').hide();
        $('.comofunciona').hide();
        $('#part-geral').clearFields();
    }, function() {
        $('.suplementar').hide();
        $('.updates').fadeIn();
        $('.api-content').hide();
        $('.comofunciona').fadeIn();
    });

    $('a.api').toggle( function() {
        $('.api-content').fadeIn();
        $('.updates').hide();
        $('.suplementar').hide();
        $('.comofunciona').hide();
    }, function() {
        $('.api-content').hide();
        $('.updates').fadeIn();
        $('.suplementar').hide();
        $('.comofunciona').fadeIn();
    });

    $('.api-content .close').click(function(){
        $('a.api').trigger('click');
    });


    $('.inVideo').click( function() {
        $('.space .video').show();
        $('.space .foto').hide();
        return false;
    });

    $('.inFoto').click( function() {
        $('.space .video').hide();
        $('.space .foto').show();
        return false
    });

    $('#nome').click( function() {
        $('.telefone').fadeIn();
        $('.newPassword').fadeIn();
        return false
    });

    $('a.fechar').click( function(){
        $('#part-geral').clearFields();
        $('.suplementar').hide();
        $('.updates').fadeIn();
    });



    $('.participe a.votar').on("click",function(){
        var url = $(this).attr('href');
        var _clicado_ = $(this)
        _clicado_.attr('disabled','disabled');
        $.get(url, function(data){
            var pData = $.parseJSON(data);
            _clicado_.parent().parent().find(".counter").html(pData.score);
            _clicado_.removeAttr('href');
            _clicado_.find('div.curtir').addClass("voted");
        });

       return false;
    });


    var showNeedLogin = function(obj, msg){
        // var botaoentrar = $('#menu .entrar a');
        // console.log( obj );
        var cont = "Você precisa <a href='/auth/login/'>efetuar o login</a> para votar!";
        if (msg != "" && msg != null) {
            cont = msg;
        }
        var options = {
            'content'      : cont,
            'title'     : "É necessário efetuar login",
            'animation' : true,
            'placement' : "right",
            'trigger'   : "manual"
        }
        obj.popover(options);
        obj.popover('show');

        window.setTimeout(function(){
            obj.popover('hide');
        },10000);
    };


    var installNeedLoginTrigger = function(){
        $('.participe a.need').on("click",function(){

            showNeedLogin($(this));

            return false;
        });
    };

    var updateall = function(){

        $('.timeline').masonry({
            itemSelector: '.update',
            gutterWidth: 60,
        });

        $(".timeline>.update").each(function(){

            var posLeft = $(this).css("left");

            if(posLeft == "0px") {
                $(this).find('.seta').addClass('esquerda');
            } else {
                $(this).addClass('direita');
                $(this).find('.seta').addClass('direita');
            }
        });

        installNeedLoginTrigger();
    };

    updateall();

    $('.govresp.remote').click(function(){
        // console.log( $(this).attr('data-id') );
        var _did = $(this).attr('data-id');
        var _oid = $(this).attr('data-oid');
        var url = "/monitore/obra/part/"+_oid+"/"+_did
        var _resp_ = $(this);

        $.get(url, function(data){
            _resp_.fadeOut('slow', function(){
                $('.timeline').masonry('destroy');
                _resp_.next().append(data);
                // $('.updates').trigger('create');
                $('video').mediaelementplayer();
                updateall();
            });
        });

        // $(this).remove();

    });

    $('.unico .updates .timeline').masonry('destroy');

    var altura = $('.info').height();
    $('.updates').css("min-height", altura);
    $('.suplementar').css("min-height", altura);
    $('.api-content').css("min-height", altura);

    $(".more").click(function(){
        var o = $('.more-content');
        if(o.hasClass('fechado')){
            o.switchClass("fechado","aberto", 600);
            $(this).html('-');
        }else{
            o.switchClass("aberto","fechado", 600);
            $(this).html('+');
        }

    });

    $('.empcontratadas').popover({
        'placement': 'left',
        'trigger'  : 'hover'
    });




});
