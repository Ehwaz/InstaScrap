$(document).ready(function(){
    // Handling modal's 'close' button
    $("#modal-close-button").click(function(){
        $('#myModal').modal('hide');
    });

    // Handling modal's 'scrap' button
    $("#modal-scrap-button").click(function(){
        var cur_button = $(this)
        // Accessing post-id using data attribute interface returns post-id of previous modal content.
        //var post_id = cur_button.data('post-id');
        var post_id = cur_button.attr('data-post-id');
        var new_state;
        if (cur_button.text() == "Scrapped") {
            new_state = 'off';
        } else if (cur_button.text() == "Scrap") {
            new_state = 'on';
        }
        $.ajax({
            type: "POST",
            url: CHANGE_SCRAP_URL,
            dataType: "json",
            data: { 'postId' : post_id,
                    'state' : new_state},
            success: function (data) {
                // Variable 'what' is not button! We need to access 'cur_button' variable from closure scope.
                // (This success function itself is closure.)
                var what = $(this)

                if (data['result_state'] == 'on') {
                    cur_button.text('Scrapped');  // result state is 'on',
                } else if (data['result_state'] == 'off') {
                    cur_button.text('Scrap');  // result state is 'off',
                }
            }
        });
    });

    // Ref: https://docs.djangoproject.com/en/1.9/ref/csrf/#ajax
    var csrftoken = Cookies.get('csrftoken');   // Using Javascript Cookie library
    function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Handling 'Load more' button
    function loadMorePosts(which_post, last_post_id) {
        $.ajax({
            type: "GET",
            url: LOAD_MORE_URL,
            dataType: "json",
            data: { 'lastPostId' : last_post_id,
                    'whichPost' : which_post},
            success: function (data) {
                console.log(data);
                for (var rowIdx = 0; rowIdx < Object.keys(data).length; rowIdx++) {
                    var rowHtml = '<div class=\"row\"></div>';
                    $('.post-container').append(rowHtml);

                    var aRow = data[rowIdx]
                    for (var postIdx in aRow) {
                        var postHtml = '<div class="col-md-4 portfolio-item"><a class="liked-post" data-insta-post-id="' + aRow[postIdx]["instagramPostId"];
                        postHtml += '" data-toggle="modal" href="#myModal">\n<img class="img-responsive" src="'
                        postHtml += aRow[postIdx]["fullResUrl"] + '" width="300" height="300" alt="">\n</a>\n</div>'

                        $('.post-container .row').last().append(postHtml);
                    }
                }
            }
        });
    };

    $("#scrappedPostLoadButton").click(function(){
        var last_post = $('.liked-post').last();
        var last_post_id = last_post.attr('data-insta-post-id');

        loadMorePosts('scrapped', last_post_id);
    });

    $("#likedPostLoadButton").click(function(){
        console.log("Hello!");
        var last_post = $('.liked-post').last();
        var last_post_id = last_post.attr('data-insta-post-id');

        loadMorePosts('liked', last_post_id);
    });
    // Handling 'Load more' button end

    // Handling post showing modal
    $('#myModal').on('show.bs.modal', function (event) {
        console.log("Modal show.bs.modal");

        var modal = $(this);
        var div = $(event.relatedTarget);
        var post_id = div.data('insta-post-id');
        $.ajax({
            type: "GET",
            url: GET_POST_URL,
            dataType: "json",
            data: { "instagramPostId" : post_id },
            success: function (data) {
                console.log(data);

                // Those 3 values must be synced.
                padding_css = "20px 30px";
                dialog_width = data["fullResWidth"] + 20 * 2;
                dialog_height = data["fullResHeight"] + 30 * 2;

                if ($(window).width() > dialog_width) {
                    $('.modal-dialog').css('width', dialog_width);
                }
                if ($(window).height() > dialog_height) {
                    $('.modal-dialog').css('height', dialog_height);
                }
                $('.modal-body').css("padding", padding_css);

                $('#modal-image-img').attr("src", data["fullResUrl"]);
                $('#modal-image-img').attr("width", data["fullResWidth"]);
                $('#modal-image-img').attr("height", data["fullResHeight"]);
                $('#modal-image-a').attr("href", data["instagramLink"]);
                $('#modal-image-author').text(data["authorName"]);
                var before = $('#modal-image-author').attr("href")
                $('#modal-image-author').attr("href", before + data["authorName"]);
                $('#modal-image-caption').html(data["caption"]);
                if (data["isScrapped"] == false) {
                    $('#modal-scrap-button').text("Scrap");
                    $('#modal-scrap-button').removeClass("active");
                    $('#modal-scrap-button').attr("aria-pressed", "false");
                } else {
                    $('#modal-scrap-button').text("Scrapped");
                    $('#modal-scrap-button').addClass("active");
                    $('#modal-scrap-button').attr("aria-pressed", "true");
                }
                $('#modal-scrap-button').attr("data-post-id", data['instagramPostId']);
                }
            });
        var photo = modal.find('.modal-body img');
        console.log(photo.attr("src"));
    });
    /*
    $('#myModal').on('shown.bs.modal', function (event) {   });
    $('#myModal').on('hide.bs.modal', function (event) {   });
    $('#myModal').on('hidden.bs.modal', function (event) {   });
    */
    // Handling post showing modal end
});

// ResponsiveBootstrapToolkit: enable developer to handle Bootstrap's resizing event.
// using IIFE to import & use javascript library.
(function($, viewport){
    var biggerThanMdWidth, biggerThanMdHeight;
    var biggerSet = false;
    var resetModalDialogSize = function() {
        // Executes only in XS breakpoint
        if(viewport.is('<sm')) {
            //console.log('Size is smaller than sm!');
            if (biggerSet == false) {
                biggerThanMdWidth = $('.modal-dialog').css("width");
                biggerThanMdHeight = $('.modal-dialog').css("height");
                biggerSet = true;
            }
            $('.modal-dialog').css("width", "auto");
        }
        if(viewport.is('>=sm')) {
            //console.log('Size is bigger than or equal to sm!');
            if (biggerSet == true) {
                $('.modal-dialog').css("width", biggerThanMdWidth);
            }
        }
    };
    // Execute code each time window size changes
    $(window).resize(
        viewport.changed(function() {
            resetModalDialogSize();
        })
    );
})(jQuery, ResponsiveBootstrapToolkit);
