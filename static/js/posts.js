container = null
authen = false
last_loaded = 0
t = null
user = null

$(document).ready(function(){
    container = $('#post-container')
    // Check wether the user has scrolled to the bottom of the page and if they have, try to load more posts 
    $(window).scroll(function(){
        if(Math.ceil($(window).scrollTop() + $(window).height()) >= Math.round($(document).height())) {
            load_posts(auth=authen, tag=t, profile_id=user)
        }
    });
})

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // This makes the scroll animated
    });
}

function load_posts(auth=true, tag = null, profile_id=null) {
    t = tag
    authen = auth
    logged_user = +logged_user
    url = '/api/get-posts/'
    new_html = ""
    data= {'l':last_loaded}
    if(t!=null) {   
        url = url + String(t).replace('#', '')
        data = {'l':last_loaded,'tag':tag}
    } else if(profile_id!=null) {
        data={'l':last_loaded, 'tag':null, 'user_p':profile_id}
        user=profile_id
    }
    $.ajax({
        url: url,  
        type: 'GET',
        data: data,
        success: function(data) {
            container.val('')
            data.forEach(post => {
                new_html += get_post_html(post, url_profile, auth)
            });
            container.append(new_html)
            last_loaded += data.length
            
            $('.reactions .btn').off('click').one('click', function() {btn_clicked($(this))})
            $('.react-btn').off('click').one('click', function() {btn_clicked($(this))})
            $('.del-btn').off('click').one('click', function() {btn_clicked($(this))})
            if(authen=='False') {
                $('.reactions .btn').prop('disabled', true)
                console.log('disabling: ' + authen)
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var errorMessage = jqXHR.responseJSON && jqXHR.responseJSON.message;
            console.error('Error: ' + (errorMessage || textStatus));
        }
    });  
}

function up_and_post(post) {
    posthtml = get_post_html(post, url_profile)
    container.prepend(posthtml)
    $('#'+post.id + ' .reactions .btn').one('click', function() {btn_clicked($(this))})
    $('#'+post.id + ' .react-btn').one('click', function() {btn_clicked($(this))})
    $('#'+post.id + ' .del-btn').one('click', function() {btn_clicked($(this))})
    scrollToTop()
}

function btn_clicked(btn) {
    t = btn.attr('id')[0]

    id = btn.attr('id').slice(1)

    if (t=='r') {             // Comment button has been clicked
        div=$('#' + id + ' .share-react')[0]
    // Make the comment form appear/disappear
        if(div.style.display == 'none') { div.style.display = 'block' }
        else { div.style.display = 'none' }
    } else {
        btn_ajax_request(btn, t, id)
    }

    function btn_ajax_request(btn, t, id) {
        url = '/api/'
        data = {
            'id':id
        }
        if (t=='l') {
            url += 'like-post/'
        } else if (t=='s') {
            url += 'share-post/'
            btn_disable(btn)
        } else if (t=='a') {
            url += 'react-post/'
            btn_disable(btn)
            commentary = $("#c"+id).val()
            data['commentary'] = commentary
        } else if (t=='d') {         
            btn_disable(btn)
            url += 'del-post/'
        }
        console.log('btn id: ' + data.id)
        $.ajax({
            url: url,  
            type: 'POST',  
            data: data,
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            success: function(data) {
                btn_time_out(btn)
                if(t=='a') {
                    up_and_post(data.post)
                 // Getting the whole comment div to disappeaar
                    $("#c"+id).val('')
                    div=btn.parent().parent()
                    div.css('display', 'none')
                } else if (t == 'd') {
                    $('#'+id).remove()
                } else if (t == 'l') {
                    console.log('Like btn clicked, user_in: '+data.user_in)
                    if(data.user_in) {
                        btn.text('Unlike (' + data.Liked + ')')
                        btn.removeClass('btn-outline-primary')
                        btn.addClass('btn-outline-secondary')
                    } else {
                        btn.text('Like (' + data.Liked + ')')
                        btn.removeClass('btn-outline-secondary')
                        btn.addClass('btn-outline-primary')
                    }
                    
                } else if (t == 's') {
                    console.log('Shared with ' + btn.id)
                    up_and_post(data.post)
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                var errorMessage = jqXHR.responseJSON && jqXHR.responseJSON.message;
                console.error('Error: ' + (errorMessage || textStatus));
            }
        });   
    }
}


function btn_disable(btn) {
    btn.off()
    btn.prop('disabled', true);            
    btn.addClass('disabled')
}

function btn_time_out(btn, timeout=500){
    btn = btn
    setTimeout(function() {
        btn.prop('disabled', false);
        btn.removeClass('disabled')
        btn.one('click', function() {btn_clicked(btn)})
    }, timeout);
}


// -------------------------------------
// -------     POST  CARD HTML ---------
// -------------------------------------

function get_post_html(post, url_profile) {
    timeSince(post.created)
    url_profile=url_profile.replace('[object Object]', '')

    try {
        premium = ''
        if(post.author.premium) {premium = `&nbsp;&nbsp;<img src='/static/img/crown.png' class='premium_crown'>`}
        reply = '<h6><a href="'+url_profile+'/'+post.author.id+'"> @'+post.author.username+'</a>'+ premium +'<br><small class="text-muted">'
        if (post.reply_to != null) {
            if (post.just_a_share) { reply += ' shared'}
            else { reply += ' replied to '}
            reply +='@' + post.reply_to.author.username
        } 
        reply += '' + timeSince(post.created) + ' ago: '
        
        liked = ''

        if(post.liked.includes(logged_user)) { liked+= "<button id='l"+ post.id +"' class='btn btn-outline-secondary'>Unlike ("+post.liked.length+')</button>'}
        else {liked+= `<button id='l`+ post.id +`' class="btn btn-outline-primary">Like (`+post.liked.length+`)</button>`}

        reply_post = ''
        if(post.reply_to != null) { reply_post = get_reply_html(post.reply_to, url_profile) }
        

        if(logged_user == post.author.id) delete_btn = `<div class='del-icon'><button id='d`+ post.id +`' class='btn btn-outline-secondary del-btn'><img src='`+ del_icon +`' class='img_del' style='dislpay:none'></button></div>`
        else delete_btn = ''

        return `<div class="card card-post" id="`+post.id+`" style="width: 100%; margin: 5px;">
                <div class="card-body"><div class='card-body-h'>
                    <div class='post-author'>`+reply+`</small></h6></div>`+ delete_btn +`</div>
                    <p class="card-text">`+post.body+`</p>
                    `+ reply_post +`
                    <hr>
                    <small class="reactions">`+liked+`
                        <button class="btn btn-outline-primary" id="r`+post.id+`">Comment</button>
                        <button class="btn btn-outline-primary" id="s`+post.id+`">Share</button>
                    </small>
                    <div class="share-react" style="display: none;">
                        <form id="share-react-form"><textarea class="form-control react-input" id="c` + post.id + `" placeholder="Write your comment... "></textarea>
                            <button class="btn btn-primary react-btn" id="a` + post.id + `">Comment</button>
                        </form>
                    </div>
                </div>
            </div>`
    } catch (error) {
        console.log(error)
        return `<div class="card" id="post-error" style="width: 100%; margin: 5px;>
                    <div class="card-body"><div class="card-title">
                        We're sorry, but there was an error while loading this post
                    </div></div>
                </div>`
    }
}

function get_reply_html(post, url_profile) {
    try {
        premium = ''
        
        if(post.author.premium) {premium = `&nbsp;&nbsp;<img src='/static/img/crown.png' class='premium_crown'>`}
        return `<div class="card card-in-card" id="`+post.id+`" style="font-size:17px">
                    <div class="card-body"><a href="`+url_profile + post.author.id +`">@`+post.author.username+`</a>`+ premium +`<small class="text-muted"> `+timeSince(post.created)+` ago</small>
                        <hr>
                        <p class="card-text">`+post.body+`</p>
                    </div>
                </div>`
    } catch (error) {
        console.log(error)
        return `<div class="card" id="post-error" style="width: 100%; margin: 5px;>
                    <div class="card-body"><div class="card-title">
                        We're sorry, but there was an error while loading this post
                    </div></div>
                </div>`
    }
}


function timeSince(timezone) {
    let currentTime = new Date()
    p_date = timezone.split('T')[0].split('-')
    p_time = timezone.split('T')[1].split(':')
    let postTime = new Date(year=p_date[0], month = p_date[1]-1, day=p_date[2], hours=p_time[0], minutes=p_time[1])
    dif = currentTime.getUTCFullYear() - postTime.getFullYear()
    if(dif > 1 || (dif == 1 && currentTime.getUTCMonth() >= postTime.getMonth())) return dif + ' years'
    dif = Math.abs(currentTime.getUTCMonth() - postTime.getMonth())
    if(dif > 1 || (dif == 1 && currentTime.getUTCDate() >= postTime.getDate())) return dif + ' months'
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if(currentTime.getUTCDate()<postTime.getDate()) dif = currentTime.getUTCDate() + (days_in_month[postTime.getMonth()]-postTime.getDate())
    else dif = currentTime.getUTCDate() - postTime.getDate()
    if(dif > 1 || (dif == 1 && currentTime.getUTCHours() >= postTime.getHours())) return dif + ' days'
    dif = Math.abs(currentTime.getUTCHours() - postTime.getHours())
    if(dif > 1 || (dif == 1 && currentTime.getUTCMinutes() >= postTime.getMinutes())) return dif + ' hours'
    return (Math.abs(currentTime.getUTCMinutes() - postTime.getMinutes())) + ' minutes'
}