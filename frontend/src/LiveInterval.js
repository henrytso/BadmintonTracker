import LiveCourt from "./LiveCourt";

function LiveInterval(props) {
    const getDisplayTime = (dtString) => {
        const hours = dtString.substring(11, 13) % 12;
        const minutes = dtString.substring(14, 16);

        return `${hours}:${minutes}`;
    }

    return (
        <div className="live-interval">

            <div className="live-interval-time-block">
                <div>
                    {`Live Interval id: ${props.id}`}
                </div>
                <div>
                    <br></br>
                    {getDisplayTime(props.start)}
                    <br></br>
                    -
                    <br></br>
                    {getDisplayTime(props.end)}
                </div>
            </div>

            <div className="live-interval-courts-block">
                {props.courtIds.map(courtId =>
                    <LiveCourt
                        key={`${props.id}-${courtId}`}
                        id={`${props.id}-${courtId}`}
                        rerenderSwitch={props.rerenderSwitch}
                    />
                )}
            </div>

        </div>
    );
}

export default LiveInterval;