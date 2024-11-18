import { useState, useEffect } from 'react';
import { useDroppable } from "@dnd-kit/core";

import "./style.css";
import LivePlayer from "./LivePlayer";

function LiveCourt(props) {
    const { isOver, setNodeRef } = useDroppable({
        id: props.id,
    });
    const style = {
        background: isOver ? 'moccasin' : undefined,
    };

    const [players, setPlayers] = useState(null);
    const [rerenderSwitch, setRerenderSwitch] = useState(props.rerenderSwitch);

    useEffect(() => {
        const fetchIntervalCourtPlayers = async () => {
            const [intervalId, courtId] = props.id.split('-');
            const response = await fetch(`http://localhost:8000/api/signups/${intervalId}/${courtId}/`);
            const data = await response.json();
            setPlayers(data);
        }
        fetchIntervalCourtPlayers();
    }, [props.rerenderSwitch]);

    return (
        <div className="live-court" ref={setNodeRef} style={style} rerenderSwitch={rerenderSwitch}>
            <div className="live-court-header">
                {/* LiveCourt id: {props.id} */}
                {`Court ${props.id.split('-')[1]}`}
            </div>

            <div className="live-court-players-list">
                {players &&
                    players.map(player =>
                        <LivePlayer
                            key={player.id}
                            id={player.id}
                            parentId={props.id}
                            name={`${player.first_name} ${player.last_name}`}
                        />
                    )
                }
            </div>
        </div>
    );
}

export default LiveCourt;