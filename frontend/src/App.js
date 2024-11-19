import React, { useEffect, useState } from 'react';
import { DndContext } from '@dnd-kit/core';

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

        if (over === null || active.data.current.parentId === over.id) {
            return;
        }

        const playerId = active.id;
        const [oldIntervalId, oldCourtId] = active.data.current.parentId.split('-').map(s => parseInt(s));
        const [newIntervalId, newCourtId] = over.id.split('-').map(s => parseInt(s));

        const tryRemoveSignup = async () => {
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

                if (!response.ok) {
                    const data = await response.json();
                    const errorMsg = data.error;
                    throw new Error(errorMsg);
                }
            }

            if (active.data.current.parentId !== "bank") {
                await removeSignup(oldIntervalId, oldCourtId);
            }
        }

        const tryCreateSignup = async () => {
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

                if (!response.ok) {
                    const data = await response.json();
                    const errorMsg = data.error;
                    throw new Error(errorMsg);
                }
            };

            if (over.id !== "bank") {
                await createSignup(newIntervalId, newCourtId);
            }
        }

        // Only need to remove old signup after a successful create.
        // e.g. Unable to create signup in a full 4-person court -> don't remove previous signup.
        tryCreateSignup()
            .then(() => tryRemoveSignup())
            .then(() => setRerenderSwitch(!rerenderSwitch))
            .catch((error) => {
                console.error(error);
            })
    }
}

export default App;