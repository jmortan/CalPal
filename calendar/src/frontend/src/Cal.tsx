import { FC, useState } from 'react'
import { Calendar, dateFnsLocalizer, Event, View } from 'react-big-calendar'
import withDragAndDrop, { withDragAndDropProps } from 'react-big-calendar/lib/addons/dragAndDrop'
import { addHours, startOfHour, startOfWeek} from 'date-fns'
import format from 'date-fns/format'
import parse from 'date-fns/parse'
import getDay from 'date-fns/getDay'
import enUS from 'date-fns/locale/en-US'
import 'react-big-calendar/lib/addons/dragAndDrop/styles.css'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import './css/Cal.css'


interface calProps {
  onMonthChange: (range: Date[] | { start: Date; end: Date; }, view?: View | undefined) => void | undefined,
}

const Cal: FC<calProps> = ({onMonthChange}: calProps) => {
  const [events, setEvents] = useState<Event[]>([
   
  ])

  const onEventResize: withDragAndDropProps['onEventResize'] = data => {
    const { start, end } = data

    setEvents(currentEvents => {
      const firstEvent = {
        start: new Date(start),
        end: new Date(end),
      }
      return [...currentEvents, firstEvent]
    })
  }

  const onEventDrop: withDragAndDropProps['onEventDrop'] = data => {
    // console.log(data)
  }

  return (
    <DnDCalendar
      defaultView='month'
      views={['month']}
      events={events}
      localizer={localizer}
      onRangeChange={onMonthChange}
      onEventDrop={onEventDrop}
      onEventResize={onEventResize}
      resizable
      style={{ height: '100vh' }}
    />
  )
}

const locales = {
  'en-US': enUS,
}
const endOfHour = (date: Date): Date => addHours(startOfHour(date), 1)
const now = new Date()
const start = endOfHour(now)
const end = addHours(start, 2)
// The types here are `object`. Strongly consider making them better as removing `locales` caused a fatal error
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales,
})
//@ts-ignore
const DnDCalendar = withDragAndDrop(Calendar)

export default Cal