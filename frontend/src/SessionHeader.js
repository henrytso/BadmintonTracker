

function SessionHeader(props) {
    const formatDate = (dtString) => {
        const date = new Date(dtString.replace(' ', 'T'));

        const options = {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        };

        return new Intl.DateTimeFormat('en-US', options).format(date);
    };

    const formatTime = (dtString) => {
        const date = new Date(dtString.replace(' ', 'T'));

        const options = {
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
        };

        return new Intl.DateTimeFormat('en-US', options).format(date);
    };

    return (
        <div className="session-header">
            <h1>
                {`Session id: ${props.sessionId} | ${props.centerName}`}
            </h1>
            <h2>
                {`${formatDate(props.start)} | ${formatTime(props.start)} - ${formatTime(props.end)}`}
            </h2>
        </div>
    );
}

export default SessionHeader;