!function(t){"use strict";t(document).on("click",".like_button",(function(){var e=t(this),n=e.attr("data-post-id"),a=e.attr("data-nonce"),i=e.attr("data-iscomment"),o,s=(o=t("1"===i?".like_comment-button-"+n:".like_button-"+n)).next("#like_loader");return""!==n&&t.ajax({type:"POST",url:salongLikes.ajaxurl,anync:!0,data:{action:"process_salong_like",post_id:n,nonce:a,is_comment:i},beforeSend:function(){s.show()},success:function(t){var e=t.icon,n=t.count;if(o.html(e+n),"unliked"===t.status){var a=salongLikes.like;o.prop("title",a),o.removeClass("liked")}else{var i=salongLikes.unlike;o.prop("title",i),o.addClass("liked")}s.hide()}}),!1}))}(jQuery);