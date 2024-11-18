import { useState, useEffect } from 'react';
import { useDroppable } from "@dnd-kit/core";

import "./style.css";
import LivePlayer from "./LivePlayer";

function PlayerBank(props) {
    const { isOver, setNodeRef } = useDroppable({
        id: props.id,
    });
    const style = {
        background: isOver ? 'moccasin' : undefined,
    };

    const [players, setPlayers] = useState(null);
    const [rerenderSwitch, setRerenderSwitch] = useState(props.rerenderSwitch);

    useEffect(() => {
        const fetchBankPlayers = async () => {
            const response = await fetch(`http://localhost:8000/api/signups/${props.sessionId}/bank/`);
            const data = await response.json();
            setPlayers(data);
        }
        fetchBankPlayers();
    }, [props.rerenderSwitch]);

    return (
        <div className="player-bank" ref={setNodeRef} style={style} rerenderSwitch={rerenderSwitch}>
            <div className="player-bank-header">
                Player Bank
            </div>

            <div className="player-bank-players-list">
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

export default PlayerBank;