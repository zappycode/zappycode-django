$(document).ready(function() {

  $('.datepicker').datepicker({
    format: 'dd-mm-yyyy',
    daysOfWeekHighlighted: "0",
    calendarWeeks: true,
    todayHighlight: true,
    inline: true,
    sideBySide: true,
    numberOfMonths: 1,
    showOptions: { direction: "down" }
  }).datepicker("daysOfWeekHighLighted");
});

