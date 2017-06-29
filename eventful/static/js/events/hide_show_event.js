$(function () {
    var futureBtn = $("#future-btn");
    var pastBtn = $("#past-btn");
    var allBtn = $("#all-btn");

    futureBtn.click(function () {
        $(".past").hide();
        $(".future").show();
        $(this).addClass("active");
        pastBtn.removeClass("active");
        allBtn.removeClass("active");
    });

    pastBtn.click(function () {
        $(".past").show();
        $(".future").hide();
        $(this).addClass("active");
        futureBtn.removeClass("active");
        allBtn.removeClass("active");
    });

    allBtn.click(function () {
        $(".event").show();
        $(this).addClass("active");
        pastBtn.removeClass("active");
        futureBtn.removeClass("active");
    });
});