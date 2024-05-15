export function getFirstLastDay():any {
    const currentDate = new Date();
    // Get the first day of the current month
    const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
  
    // Get the day of the week of the first day of the month (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
    const firstDayOfWeek = firstDayOfMonth.getDay();
  
    // Calculate the offset to the first Sunday of the current calendar view
    //const offsetToFirstSunday = firstDayOfWeek === 0 ? 0 : 7 - firstDayOfWeek;
  
    // Get the first Sunday of the current calendar view
    const firstSunday = new Date(firstDayOfMonth);
    firstSunday.setDate(1 - firstDayOfWeek);
  
    // Get the last day of the current month
    const lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
  
    // Get the day of the week of the last day of the month
    const lastDayOfWeek = lastDayOfMonth.getDay();
  
    // Calculate the offset to the last Saturday of the current calendar view
    const offsetToLastSaturday = lastDayOfWeek === 6 ? 0 : 6 - lastDayOfWeek;
  
    // Get the last Saturday of the current calendar view
    const lastSaturday = new Date(lastDayOfMonth);
    lastSaturday.setDate(lastDayOfMonth.getDate() + (offsetToLastSaturday));
  
    // Format the dates as strings (assuming YYYY-MM-DD format)
   return {month: currentDate.getMonth(),startDate: firstSunday,endDate: lastSaturday}
  }

  export function getDateFromPosition(canvas:any, dateRange:any, height:any, mouseX:any, mouseY:any):any {
    const rect = canvas.getBoundingClientRect();
    const offsetX = mouseX - rect.left;
    const offsetY = mouseY - rect.top + 0.8*(window.innerHeight-height);

    const daysInMonth = Math.floor((dateRange.endDate.getTime() - dateRange.startDate.getTime()) / (1000 * 60 * 60 * 24));
    const weeksInMonth = Math.ceil(daysInMonth / 7); // Calculate number of weeks
    const squareWidth = canvas.width / 7;
    const squareHeight = canvas.height/weeksInMonth;
  
    const numDays = Math.floor(offsetX / squareWidth);
    const numWeeks = Math.floor(offsetY / squareHeight);
  
    const selectedDate = new Date(dateRange.startDate);
    //console.log(selectedDate, numDays,numWeeks)
    selectedDate.setDate(selectedDate.getDate() + numDays + numWeeks * 7);
  
    return selectedDate;
  }