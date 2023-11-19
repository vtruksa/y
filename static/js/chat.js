var sk = 0

function on_send_message() { 
    event.preventDefault();
            input = $('#message-input');
        
            console.log("chats.html fce on_send_message | Send-message-btn clicked | The message is: " + open_chat.id);
            var csrf_token = $('#message-form [name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url: '/api/send-message/',
                type: 'POST',
                data: {
                    'conversation_id':open_chat.id,
                    'message': input.val(),  
                },
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                },
                success: function(data) {
                    e = document.getElementById('messages');
                    e.insertAdjacentHTML('afterbegin', "<div class='message-sent'>" + input.val() + "</div>");
                    input.val("")
                    console.log("Success")
                },
                error: function(error) {
                    input.val("")
                    console.log("Error")
                }
            })
}

function switch_active_chat(chat_id) {
    $('#convos ul li button#' + chat_opened_id).removeClass('chat-active')
    chat_opened_id = chat_id
    $('#convos ul li button#' + chat_id).addClass('chat-active')
    console.log('switched active chat')
}

function add_conversation_sidepanel(convo, to_user_id) {
    convo_list = $("#convos ul")[0]

    new_convo_html = '<li class="conversation"><button id="'+convo.id+'" class="convo" style="height: 75px; margin-bottom: 4px; margin-top: 4px;" >'
    /*if(convo.avatar.name) { new_convo_html += '<img src="'+convo.avatar.url+'" width="60px" style="border-radius: 60px;">' }
    else {*/ new_convo_html += '<img src="/media/avatars/default.png" width="60px" style="border-radius: 60px;">' //}
    new_convo_html += '<h8>&nbsp;&nbsp;'+ convo.name +'</h8></button></li>'
    
    convo_list.insertAdjacentHTML('afterbegin', new_convo_html)
}