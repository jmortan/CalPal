import { useState, useEffect, useRef } from 'react';
import { getFirstLastDay, getDateFromPosition } from './utils';
import './css/App.css';
import Cal from './Cal';
import Canvas from './canvas';
import CalTheme from './calTheme';
import axios from 'axios';

//Custom Types
type bbox = {
  minX: number
  maxX: number
  minY: number
  maxY: number
}

type Coordinate = {
  x: number;
  y: number;
};


function App() {
  //Set up states for tracking modes of calendar operation

  //monthEvents will be {eventId:bbox}, for tracking the events in the current view
  const [monthEvents, setMonthEvents] = useState<any>({});
  //dateState tracks which month we are currently in, {month: currentDate.getMonth(),startDate: firstSunday,endDate: lastSaturday} 
  const [dateState,setDateState] = useState(getFirstLastDay());
  //1 = draw, 0 = erase
  const [calMode, setCalMode] = useState(true);
  //1=should update cal theme, 0 = should not update cal theme
  const [calTheme, setCalTheme] = useState(false);
  //
  const [mousePosition, setMousePosition] = useState<Coordinate | undefined>(undefined);

  //set up Refs for accessing nonStateful elements from child components
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const canvHeight = window.innerHeight*0.74;
  const canvWidth = window.innerWidth;
  const bboxRef = useRef<bbox | undefined>(undefined);




  
 

  const onMonthChange = (range:any, view:any) => {
    let startMonth: number = range.start.getMonth();
    let endMonth: number = range.end.getMonth();
    let startDay = range.start.getDate();
    // console.log(startMonth,endMonth,startDay)
    let currMonth: number;
    if (startMonth > endMonth) {
      //three cases, Dec - Jan (start dec), Dec - Feb, nov-Jan
      if (startMonth === 10) {
        currMonth =11
      } else if (endMonth ===1) {
        currMonth = 0
      } else if (startDay === 1){
        currMonth=11
      } else {
        currMonth = 0
      }
    } else if (endMonth-startMonth > 1) {
      currMonth = startMonth+1
    } else if (startDay === 1) {
      currMonth = startMonth
    } else {
      currMonth = endMonth
    }
    setDateState({month: currMonth, startDate: range.start, endDate: range.end})
  }

  const onAddEventClick = async () => {
    const canvas = canvasRef.current;
    if (canvas && calMode && mousePosition && bboxRef.current) {
        const dataUrl = canvas.toDataURL('image/png');
        //console.log("Month is", dateState.month)
        //console.log(mousePosition)
        const currentDate = getDateFromPosition(canvas,dateState,canvHeight,mousePosition.x,mousePosition.y)
        const currBbox = bboxRef.current
        console.log("Current Bbox is: ", currBbox)
        const bboxFormat = [[currBbox.minX,currBbox.maxY],[currBbox.maxX,currBbox.minY]]
        try {
            await axios.post('/addEvent', {
                canvasData: dataUrl,
                month:dateState.month,
                date:currentDate.toDateString(),
                bbox:bboxFormat
            }).then(({data})=>{
                console.log(data)
                //"No text detected" in byte string format
                if(data==="Not detected"){
                    let ctx = canvas.getContext('2d');
                    ctx?.clearRect(bboxFormat[0][0]-5,bboxFormat[1][1]-5,bboxFormat[1][0] - bboxFormat[0][0]+10,bboxFormat[0][1] - bboxFormat[1][1]+10);
                    window.alert("Failed to recongize text, please try again!")    
                } else if (data) {
                    let months={...monthEvents};
                    months[data]=bboxFormat
                    setMonthEvents(months)
                    setCalTheme(true)
                }
            });
            //console.log('Canvas image sent successfully!');
            } catch (error) {
                let canvas:any = canvasRef.current
                if (canvas) {
                    let ctx = canvas.getContext('2d');
                    ctx?.clearRect(bboxFormat[0][0]-5,bboxFormat[1][1]-5,bboxFormat[1][0] - bboxFormat[0][0]+10,bboxFormat[0][1] - bboxFormat[1][1]+10);
                    window.alert("Failed to recognize text, please try again!")
                }
                console.error('Error sending canvas image:', error);
        }
        bboxRef.current=undefined;
      }
    }

  const onEraseClick = () => {
    let canvas:any = canvasRef.current
    const currBbox = bboxRef.current
    //console.log("Current Bbox is: ", currBbox)
    if (canvas && currBbox) {
        const bboxFormat = [[currBbox.minX,currBbox.maxY],[currBbox.maxX,currBbox.minY]]
        let ctx = canvas.getContext('2d');
        ctx?.clearRect(bboxFormat[0][0]-5,bboxFormat[1][1]-5,bboxFormat[1][0] - bboxFormat[0][0]+10,bboxFormat[0][1] - bboxFormat[1][1]+10);
    }
    setCalMode(false)
  }

  const onDrawClick = () => {
    setCalMode(true)
  }

  const pollBackend = () => {
    setInterval(function() {
        // Make a request to the backend
        axios.get('/lookGesture').then(({data}):any=>{
          //0 if not flipped, 1 if flipped
          // console.log(data)
          if (data==="Forward" || data==="Backward") {
            // console.log("Received flip")
            let buttons:Element|null= document.querySelector('.rbc-btn-group')
            if (buttons) {
              // console.log(buttons)
              let buttonArr:HTMLCollection=buttons.children
              let buttonNext:any = buttonArr[2]
              let buttonPrev:any = buttonArr[1]
              data==="Forward"?buttonNext.click():buttonPrev.click()
            }
          }
        }).catch(error => {
          // console.log("Error sending request", error)
        })
      }
    ,1000)}

  
  useEffect(() => {
      pollBackend()
  }, []);

  return (
    <div className='container'>
      <CalTheme width={window.innerWidth} height={window.innerHeight*0.2} newCalTheme={calTheme} setNewCalTheme={setCalTheme} dateState={dateState}></CalTheme>
      <button className='eraseModeButton' onClick={onEraseClick} style={{ backgroundColor: calMode ? 'white' : 'yellow' }}>Erase</button>
      <button className='drawModeButton' onClick={onDrawClick} style={{ backgroundColor: calMode ? 'yellow' : 'white' }}>Draw</button>
      <button className={calMode?'addEventModeButton addEventModeButtonDraw':'addEventModeButton addEventModeButtonErase'} onClick={onAddEventClick}>Add Event</button>
      <div className='monthDiv'></div>
      <Cal onMonthChange={onMonthChange} />
      <Canvas width={canvWidth} height={canvHeight} dateState={dateState} calMode={calMode} setNewCalTheme={setCalTheme} bboxRef={bboxRef} mousePosition={mousePosition} setMousePosition={setMousePosition} canvasRef={canvasRef} setMonthEvents={setMonthEvents} monthEvents={monthEvents} />
    </div>
  );
}

export default App
