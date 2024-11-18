import React, { useEffect, useState } from 'react';
import { DndContext } from '@dnd-kit/core';

// import PastInterval from './PastInterval';
import LiveInterval from './LiveInterval';
import PlayerBank from './PlayerBank';
import SessionHeader from './SessionHeader';

function App() {
    const sessionId = 1;

    const [sessionData, setSessionData] = useState(null);
    const [rerenderSwitch, setRerenderSwitch] = useState(false);

    const fetchSessionData = async () => {
        const response = await fetch(`http://localhost:8000/api/v2/sessiondata/${sessionId}/`);
        const data = await response.json();
        setSessionData(data);
    };

    useEffect(() => {
        fetchSessionData();
    }, []);

    return (
        <DndContext onDragEnd={handleDragEnd}>
            {sessionData &&
                <SessionHeader
                    sessionId={sessionId}
                    centerName={sessionData.centerName}
                    start={sessionData.start}
                    end={sessionData.end}
                />
            }

            {/* <div>
                {sessionData &&
                    sessionData.intervals
                        .filter(interval => interval.id < sessionData.liveIntervalId)
                        .map(interval =>
                            <PastInterval
                                key={interval.id}
                                id={interval.id}
                                start={interval.start}
                                end={interval.end}
                                courtIds={sessionData.courtIds}
                            />
                        )
                }
            </div> */}

            <PlayerBank
                key={"bank"}
                id={"bank"}
                sessionId={sessionId}
                rerenderSwitch={rerenderSwitch}
            />

            <div>
                {sessionData &&
                    sessionData.intervals
                        .filter(interval => interval.id >= sessionData.liveIntervalId)
                        .map(interval =>
                            <LiveInterval
                                key={interval.id}
                                id={interval.id}
                                start={interval.start}
                                end={interval.end}
                                courtIds={sessionData.courtIds}
                                rerenderSwitch={rerenderSwitch}
                            />
                        )
                }
            </div>
        </DndContext>
    );

    function handleDragEnd(event) {
        const { active, over } = event;

        if (over === null) {
            return;
        }

        if (active.data.current.parentId !== over.id) {
            const playerId = active.id;
            const [oldIntervalId, oldCourtId] = active.data.current.parentId.split('-').map(s => parseInt(s));
            const [newIntervalId, newCourtId] = over.id.split('-').map(s => parseInt(s));

            const removeSignup = async (intervalId, courtId) => {
                const response = await fetch(`http://localhost:8000/api/signups/`, {
                    method: "POST",
                    body: JSON.stringify({
                        "court_id": courtId,
                        "interval_id": intervalId,
                        "player_id": playerId,
                        "remove": true,
                    })
                });
                const data = await response.json();
                console.log(data);
            }

            const createSignup = async (intervalId, courtId) => {
                const response = await fetch(`http://localhost:8000/api/signups/`, {
                    method: "POST",
                    body: JSON.stringify({
                        "court_id": courtId,
                        "interval_id": intervalId,
                        "player_id": playerId,
                        "remove": false,
                    })
                });
                const data = await response.json();
                console.log(data);
            }

            const tryRemoveSignup = async () => {
                if (active.data.current.parentId !== "bank") {
                    removeSignup(oldIntervalId, oldCourtId);
                }
            }

            const tryCreateSignup = async () => {
                if (over.id !== "bank") {
                    createSignup(newIntervalId, newCourtId)
                }
            }

            // Make sure DB cursors don't overlap if removing and creating simultaneously
            tryRemoveSignup()
                .then(() => tryCreateSignup())
                .then(() => fetchSessionData())
                .then(() => setRerenderSwitch(!rerenderSwitch));
        }
    }
}

export default App;