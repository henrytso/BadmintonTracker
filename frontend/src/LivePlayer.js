import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';

function LivePlayer(props) {
    const { attributes, listeners, setNodeRef, transform } = useDraggable({
        id: props.id,
        data: {
            parentId: props.parentId
        }
    });
    const style = {
        transform: CSS.Translate.toString(transform),
    };

    return (
        <button className="live-player" ref={setNodeRef} style={style} {...listeners} {...attributes} >
            {props.name}
            {/* {`LivePlayer | id: ${props.id} | name: ${props.name}`} */}
        </button>
    );
}

export default LivePlayer;