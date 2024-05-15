import {  useEffect, useRef, Dispatch, SetStateAction, useCallback } from 'react';
import './css/calTheme.css';
import axios from 'axios';

interface CalThemeProps {
    width: number;
    height: number;
    newCalTheme: boolean;
    setNewCalTheme: Dispatch<SetStateAction<boolean>>;
    dateState: any;
  }

//We want to update cal theme 1) every time a new event is added and 2) when the month is changed
const CalTheme: React.FC<CalThemeProps>= ({ width, height, newCalTheme, setNewCalTheme, dateState }) =>{

    const canvasRef = useRef<HTMLCanvasElement>(null);
    let lastPattern:any = useRef(null);

    //Function that lets us blend between two calendar themes
    const animateTransition = useCallback((ctx:any, newPattern:any) => {
        let alpha = 0; // Opacity for fading effect
        const fadeSpeed = 0.03; // Speed of fading effect

        const animationLoop = () => {

            if (lastPattern.current) {
                // Draw the first image with reduced opacity
                ctx.globalAlpha = 1 - alpha;
                ctx.fillStyle = lastPattern.current;
                ctx.fillRect(0, 0, width, height);
            }

            // Draw the second image with increased opacity
            ctx.globalAlpha = alpha;
            ctx.fillStyle=newPattern
            ctx.fillRect(0,0,width,height)

            // Increase opacity for next frame
            alpha += fadeSpeed;

            // Check if animation is complete
            if (alpha < 1) {
                // Continue animation
                requestAnimationFrame(animationLoop);
            } else {
                // Animation complete
                lastPattern.current = newPattern
            }
        };

        // Start the animation loop
        requestAnimationFrame(animationLoop);
    },[width, height]);

    //fetch and update the theme
    const fetchTheme = useCallback(() => {
        let canvElement = canvasRef.current;
        let ctx = canvElement?.getContext("2d");
        try {
            axios.get("/monthTheme?month="+String(dateState.month)).then(
                ({data}):any=>{
                    if (data) {
                        let themeBytes = data.theme;
                        if (ctx) {
                            const img = new Image();
                            img.src = "data:image/png;base64,"+themeBytes;     
                            img.onload = () => {
                                if (ctx) {
                                    const pattern = ctx.createPattern(img, "repeat-x");
                                    if (pattern) {
                                        animateTransition(ctx,pattern);
                                    }
                                }
                            };
                        }
                        
                    }
            })

        } catch (error) {
            console.log("Error fetching/updating calendar theme: ", error)
        }
    },[dateState, animateTransition])

    

    useEffect(() => {
        fetchTheme()
    },[fetchTheme])

    useEffect(() => {
        if(newCalTheme) {
            fetchTheme()
            setNewCalTheme(false)
        }
    },[newCalTheme, fetchTheme, setNewCalTheme])

    return (
    <canvas ref={canvasRef} className='calendarTheme' height={height} width={width} />
    )

}

export default CalTheme;