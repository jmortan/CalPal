/* Credit AnkurSheel: https://github.com/AnkurSheel/react-drawing-interaction/tree/master */

import { useCallback, useEffect, useState, Dispatch, SetStateAction } from 'react';
import axios from 'axios';
import './css/canvas.css';

interface CanvasProps {
    width: number;
    height: number;
    dateState: any;
    calMode: boolean;
    setNewCalTheme: Dispatch<SetStateAction<boolean>>;
    bboxRef: any;
    mousePosition:any;
    setMousePosition:any;
    canvasRef:any;
    setMonthEvents:any;
    monthEvents:any;

}

type Coordinate = {
    x: number;
    y: number;
};


const Canvas = ({ width, height, dateState, calMode, setNewCalTheme, bboxRef, mousePosition,setMousePosition,canvasRef,setMonthEvents,monthEvents }: CanvasProps) => {
    const [isPainting, setIsPainting] = useState(false);

    
    const updateBbox = (coordinates: Coordinate) => {
        //If bbox initiated, compare to find new Bbox
        if (bboxRef.current===undefined) {
            //console.log("Setting curr bbox")
            bboxRef.current={minX:coordinates.x,maxX:coordinates.x,minY:coordinates.y,maxY:coordinates.y}
        } else {
            //console.log("Updating bbox")
            let a = bboxRef.current;
            bboxRef.current={minX: Math.min(a.minX,coordinates.x), maxX: Math.max(a.maxX,coordinates.x), minY: Math.min(a.minY, coordinates.y), maxY: Math.max(a.maxY, coordinates.y)}
        }
    }


    const startPaint = useCallback((event: MouseEvent) => {
        const coordinates = getCoordinates(event);
        if (coordinates && calMode) {
            setMousePosition(coordinates);
            setIsPainting(true);
            //console.log("startPaint",bboxRef.current)
            updateBbox(coordinates);
        }
    }, [calMode]);

    useEffect(() => {
        if (!canvasRef.current) {
            return;
        }
        const canvas: HTMLCanvasElement = canvasRef.current;
        canvas.addEventListener('mousedown', startPaint);
        return () => {
            //console.log("Removing event listener")
            canvas.removeEventListener('mousedown', startPaint);
        };
    }, [startPaint]);

    // fetch new canvas element when currMonth updates
    const fetchMonth = useCallback(async () => {
        if (!canvasRef.current) {
            return;
        }
        const canvas: HTMLCanvasElement = canvasRef.current;
        const context = canvas.getContext('2d');
        if (context) {
            //console.log(dateState.month)
            let url = "/monthEvents?month="+String(dateState.month);
            try {
                await axios.get(url).then(({data}):any=>{
                //console.log(data);
                if (data) {
                    let canvImg = data.month;
                    let bb_dict = data.bbox;
                    if (canvImg==="Wlcxd2RIaz0=") {
                        context.clearRect(0,0,width,height)
                    } else {
                        context.clearRect(0,0,width,height)
                        var img = new Image();
                        img.src = canvImg;
    
                        img.onload = function() {
                            context.drawImage(img, 0, 0);
                        };
                    }
                    setMonthEvents(bb_dict)
                }
                
                })
            } catch (error) {
                console.log(error)
            }

      }}, [dateState]) 

    useEffect(()=>{
        fetchMonth()
    },[fetchMonth])

    const paint = useCallback(
        (event: MouseEvent) => {
            if (isPainting && calMode) {
                const newMousePosition = getCoordinates(event);
                if (mousePosition && newMousePosition) {
                    drawLine(mousePosition, newMousePosition);
                    setMousePosition(newMousePosition);
                    updateBbox(newMousePosition);
                }
            }
        },
        [isPainting, mousePosition]
    );

    useEffect(() => {
        if (!canvasRef.current) {
            return;
        }
        const canvas: HTMLCanvasElement = canvasRef.current;
        canvas.addEventListener('mousemove', paint);
        return () => {
            canvas.removeEventListener('mousemove', paint);
        };
    }, [paint]);

    const exitPaint = useCallback(() => {
        setIsPainting(false);
        //setMousePosition(undefined);
    }, []);

    useEffect(() => {
        if (!canvasRef.current) {
            return;
        }
        const canvas: HTMLCanvasElement = canvasRef.current;
        canvas.addEventListener('mouseup', exitPaint);
        canvas.addEventListener('mouseleave', exitPaint);
        return () => {
            canvas.removeEventListener('mouseup', exitPaint);
            canvas.removeEventListener('mouseleave', exitPaint);
        };
    }, [exitPaint]);

    

    const getCoordinates = (event: MouseEvent): Coordinate | undefined => {
        if (!canvasRef.current) {
            return;
        }

        const canvas: HTMLCanvasElement = canvasRef.current;
        return { x: event.pageX + 3, y: event.pageY - canvas.offsetTop - 0.9*(window.innerHeight-height)};
    };

    const drawLine = (originalMousePosition: Coordinate, newMousePosition: Coordinate) => {
        if (!canvasRef.current) {
            return;
        }
        const canvas: HTMLCanvasElement = canvasRef.current;
        const context = canvas.getContext('2d');
        if (context) {
            context.strokeStyle = 'red';
            context.lineJoin = 'round';
            context.lineWidth = 1.5;

            context.beginPath();
            context.moveTo(originalMousePosition.x, originalMousePosition.y);
            context.lineTo(newMousePosition.x, newMousePosition.y);
            context.closePath();

            context.stroke();
        }
    };

    const handleBoundingBoxClick = async(eventId:string) => {
        if(!calMode) {
            //console.log("deleting event")
            let eventBbox = monthEvents[eventId];
            const { [eventId]: removedKey, ...rest } = monthEvents;
            const canvas = canvasRef.current;
            if (canvas) {
                const context=canvas.getContext('2d')
                if (context) {
                    context.clearRect(eventBbox[0][0]-5,eventBbox[1][1]-5,eventBbox[1][0] - eventBbox[0][0]+10,eventBbox[0][1] - eventBbox[1][1]+10)
                    setMonthEvents(rest)
                    try {
                        await axios.post('/modifyEvent',{
                            month: dateState.month,
                            event_id:eventId,
                            canvasData:canvas.toDataURL('image/png')
                        }).then(({data})=>{
                            setNewCalTheme(true)
                        })

                    } catch {
                        console.log("delete failed")
                    }
                }
            }

        }
    }

    return (<div className='draw centered'>
        <canvas ref={canvasRef} height={height} width={width} />
        {Object.entries(monthEvents).map(([eventId,bbox]:[any,any]) => (
        <div
          key={eventId}
          style={{
            position: 'absolute',
            left: bbox[0][0],
            top: bbox[1][1],
            width: bbox[1][0] - bbox[0][0],
            height: bbox[0][1] - bbox[1][1],
            cursor: 'pointer',
            pointerEvents: 'auto', // Enable click events on the div
            opacity: 1, // Make the div invisible
          }}
          onClick={() => handleBoundingBoxClick(eventId)}
        ></div>
      ))}

        </div>);
};

Canvas.defaultProps = {
    width: window.innerWidth,
    height: window.innerHeight,
};

export default Canvas;