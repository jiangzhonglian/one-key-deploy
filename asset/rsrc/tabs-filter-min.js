jQuery((function(a){a(".tab_content .tab").first().addClass("active"),a(".tabs ul.tab_li > li").click((function(){a(this).addClass("active titleColor").removeClass("textColor"),a(this).siblings().removeClass("active titleColor").addClass("textColor"),$(".tab_content .active").removeClass("active");var t=$(this).data("index");$("."+t).addClass("active")})),a(".salong_tabs_filters input").change((function(){var t=a(this).data("url"),i,s=a(this).attr("value").split("-"),e=s[0],l=s[1],n=a("#"+e+"_"+l),o=n.find(".ajax_tabs_list"),r=n.find(".salong_tabs_filters"),d=n.find("#salong_tabs_wrap"),c;return o.append('<div class="loading"></div>'),n.find("a.more").attr("href",t),a.ajax({url:salong_tab_loadmore_params.ajaxurl,data:r.serialize(),dataType:"json",type:"POST",success:function(t){d.html(t.content),o.children(".loading").remove(),a("img.thumb").lazyload({effect:"fadeIn",failure_limit:10})}}),!1}))}));