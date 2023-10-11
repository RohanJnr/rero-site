import { createSignal } from "solid-js";
import { app } from "../firebasestuff/client";
import { getFirestore, collection, query, where, getDocs, onSnapshot } from "firebase/firestore";

function CodeLogs() {

    const regex = /(\S+)\s+\[(.*?)\]\s+(.+)/;
    const [logs, setLogs] = createSignal([])

    const db = getFirestore(app);
    const q1 = query(collection(db, "submissions"), where("userEmail", "==", "roalleti@gmail.com"));

    const unsubscribe = onSnapshot(q1, (querySnapshot) => {
        querySnapshot.forEach((doc) => {
            const data = []
            doc.data().logs.forEach(log => {
                const match = log.match(regex);

                if (match) {
                    const timestamp = match[1];

                    
                    const dateTimeString = new Intl.DateTimeFormat('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                    }).format(new Date(timestamp * 1000));

                    const module = match[2];
                    const text = match[3];

                    data.push({
                        "timestamp": dateTimeString,
                        module,
                        text,
                        fullText: `${dateTimeString}\t[${module}]\t${text}`
                    })
                }
            })
            setLogs(() => data)
        });
      });

    return (
        <div class="max-h-[50vh] bg-[#f5f5f5] col-span-2 p-5 rounded overflow-hidden">
            {/* hello: <Show when={robot()}>{robot().fullName}</Show> */}
            <div class="overflow-y-scroll h-full w-full flex flex-col items-start justify-start gap-3">
                <For each={logs()}>
                    {(item) => <p class="flex justify-start items-start gap-2"><span class="text-[#35353577]">{item.timestamp}</span><span class="text-[#4827ff]">[{item.module}]</span><span class="text-text-light font-medium">{item.text}</span></p>}
                </For>
            </div>
        </div>
    )
}

export default CodeLogs