    $(document).ready(function() {
        prepareBtns()
    })

    function prepareBtns() {
        $('#post-btn').one().click(function() {   
            console.log('posting')
            input = $('#form-text')
            console.log(input.val())
            $.ajax({
                 url: '/api/post-post',  
                 type: 'POST',
                 data: {
                   'post':input.val()
                 },
                  beforeSend: function(xhr, settings) {
                  xhr.setRequestHeader("X-CSRFToken", csrf_token);
                  },
                  success: function(data) {
                     up_and_post(data)
                     input.val('')
                  },
                 error: function(error) {
                     console.log('Error: ' + error)
                  }
            }); 
        },) 
    }