$(document).ready(function () {
    $('div.job_controls a').click(function (e) {
        var url = $(this).attr('href');
	var size = $(this).attr('class');
	var current = $(this).attr('id')
        var tmp = $(this).parents().siblings('div.job_info');
	
	if (current == "hide")
	{
		tmp.animate( {'height':'0'}, 500);
		tmp.html('');

		tmp.removeClass();
		tmp.addClass("job_info");
	}
	else if (!tmp.hasClass(current))
	{
		tmp.animate( {'height':size}, 500);
		tmp.html("<h1>Loading...</h1>");
		tmp.load(url);

		tmp.removeClass(); 
		tmp.addClass("job_info");
		tmp.addClass(current);
	}
	else
	{
		tmp.load(url);
	}

        e.preventDefault();
    })
});
