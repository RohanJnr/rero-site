import {createResource, createSignal, createEffect} from "solid-js";
import { app } from "../firebasestuff/client";
import { getFirestore, collection, query, where, getDocs, orderBy } from "firebase/firestore";
import { Motion, Presence } from "@motionone/solid";
import { useKeyDownEvent } from "@solid-primitives/keyboard";

import hljs from 'highlight.js'
import "highlight.js/styles/stackoverflow-light.css";

function SubmissionList(props) {

    const BASE_BACKEND_URL = "https://server.ieeeraspesu.tech"
    // CONST BASE_BACKEND_URL = "http://20.197.11.23:8000"

    const [controlIsActive, setControlIsActive] = createSignal(false)
    let wsConnection = null


    const fetchState = async () => {
        const data = await fetch(`${BASE_BACKEND_URL}/api/submission/task_status`)
        const jsonData = await data.json()
        return jsonData['status']
    }

    const [robotState, { mutate, refetch }] = createResource(fetchState);

    setInterval(refetch, 5000)

    createEffect(() => {
        if (controlIsActive()) {
            const movementKeys = ['w', 'a', 's', 'd']
            document.addEventListener("keydown", e=> {
                console.log("keydown: ", e.key)
                if (movementKeys.includes(e.key)) {
                    if (wsConnection) {
                        wsConnection.send(e.key)
                    }
                }
            })
    
            document.addEventListener("keyup", e=> {
                console.log("keyup: ", e.key)
    
                
                if (movementKeys.includes(e.key)) {
                    if (wsConnection) {
                        wsConnection.send('x')
                    }
                }
            })
        }
      });
    

    const {user} = props

    const [showCode, setShowCode] = createSignal("")
    const [showLogs, setShowLogs] = createSignal("")
    
    const [runButtonSpinner, setRunButtonSpinner] = createSignal("")
    const [stopButtonSpinner, setStopButtonSpinner] = createSignal("")

    const [taskRunning, setTaskRunning] = createSignal("")


    const fetchUserSubmissions = async () => {
        const db = getFirestore(app);
        const submissionQuery = query(collection(db, "submissions"), where("submitted_by_email", "==", user.email), orderBy("timestamp"));

        const querySnapshot = await getDocs(submissionQuery)
        const data = []
        querySnapshot.forEach((doc) => {
            const doc_data = doc.data()

            // const date = new Date(doc_data.datetime_iso);
            // doc_data["date"] = date.toLocaleString()
            data.push({id: doc.id, ...doc_data})
        });

        return data
    }

    const [data, states] = createResource(fetchUserSubmissions)

    const userSubmissionRefetch = states.refetch


    const toggleControls = async () => {
        if (controlIsActive()) {
            console.log("Shutting down manual controls.")
            if (wsConnection) {
                wsConnection.close()
                wsConnection = null
            }

            setControlIsActive(false)

        } else {
            const payload = {
                user_email: user.email
            }
    
            const myHeaders = new Headers();
            myHeaders.append("Content-Type", "application/json");
            const res = await fetch(`${BASE_BACKEND_URL}/api/submission/stop`, {
                method: "POST",
                body: JSON.stringify(payload),
                headers: myHeaders
            })
            const jsonRes = await res.json()
            if (res.status !== 200) {
                alert(`Error! Mostly permissions error, ${jsonRes['detail']}`)
                return
            }

            console.log("Turning on manual controls.")
            console.log(WebSocket)

            const ws = new WebSocket(`wss://server.ieeeraspesu.tech/controls`)
            ws.addEventListener("open", e => {
                console.log("connected")
            })

            ws.addEventListener("message", e => {
                console.log("Got message: ", e.data)
            })

            wsConnection = ws
            setControlIsActive(true)

        }
    }

    const toggleCode = id => {
        if (showCode() === id) {
            setShowCode("")
        }
        else {
            setShowCode(id)
        }
    }

    const toggleLogs = id => {
        if (showLogs() === id) {
            setShowLogs("")
        }
        else {
            setShowLogs(id)
        }
    }

    const getHighlightedCode = (code) => {
        const result = hljs.highlight(code, {language: "python"})
        return result.value
    }

    const runSubmission = async (submission_id) => {
        if (controlIsActive() === true) {
            alert("Cannot run task when manual controls are active! Please turn off manual controls before running a submissions.")
            return
        }
        setRunButtonSpinner(submission_id)
        const payload = {
            submission_id,
            user_email: user.email
        }

        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const res = await fetch(`${BASE_BACKEND_URL}/api/submission/run`, {
            method: "POST",
            body: JSON.stringify(payload),
            headers: myHeaders
        })

        const jsonRes = await res.json()
        
        if (res.status !== 200){
            alert(`Error: ${jsonRes['detail']}`)
        }

        console.log(jsonRes)

        setRunButtonSpinner("")

    }

    const stopSubmission = async (submission_id) => {
        setStopButtonSpinner(submission_id)
        const payload = {
            submission_id,
            user_email: user.email
        }

        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const res = await fetch(`${BASE_BACKEND_URL}/api/submission/stop`, {
            method: "POST",
            body: JSON.stringify(payload),
            headers: myHeaders
        })

        const jsonRes = await res.json()
        console.log(jsonRes)

        if (res.status !== 200) {
            alert(`Error: ${jsonRes['detail']}`)
        }

        setStopButtonSpinner("")
    }

    return (
        <div>
            <div class="my-10">
                <div class="rounded-lg overflow-hidden shadow-md">
                    <div class="grid grid-cols-5 w-full text-gray-700 uppercase bg-gray-50 font-bold text-xs px-6 py-3">
                        <p>submission ID</p>
                        <p>Submitted Timestamp</p>
                        <p>Submitted By</p>
                        <p>Code & Logs</p>
                        <p>Actions</p>
                    </div>

                    <For each={data()}>
                        {(item) => (
                            <div class="grid grid-cols-5 px-6 py-4 text-gray-400 font-medium text-sm border-b">
                                <p class="text-gray-800 my-auto">{item.id}</p>
                                <p class="my-auto">{item.timestamp.toDate().toString().replace(/ GMT\+\d{4} \(India Standard Time\)/, '')}</p>
                                <p class="my-auto">{item.submitted_by}</p>
                                <div class="flex justify-start items-center gap-2">
                                    <p onClick={() => toggleCode(item.id)} class="hover:cursor-pointer font-medium text-blue-600 dark:text-blue-500 hover:underline">Code</p>
                                    <p onClick={() => toggleLogs(item.id)} class="font-medium text-blue-600 dark:text-blue-500 hover:underline hover:cursor-pointer">Logs</p>
                                </div>
                                <div class="flex justify-start items-center gap-2">
                                    <button onClick={() => runSubmission(item.id)} type="button" class={taskRunning() ? 'font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 border' : 'text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2'}>{runButtonSpinner() === item.id ? (
                                        <div role="status" class="my-10">
                                            <svg aria-hidden="true" class="w-4 h-4 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                                                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
                                            </svg>
                                            <span class="sr-only">Loading...</span>
                                        </div>
                                    ) : 'Run'}</button>
                                    <button onClick={() => stopSubmission(item.id)} class="relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 focus:ring-4 focus:outline-none focus:ring-red-100">
                                        <span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white rounded-md group-hover:bg-opacity-0">
                                            Stop
                                        </span>
                                    </button>
                                </div>
                                <Presence>
                                    <Show when={showCode() === item.id}>
                                            <Motion.div
                                            initial={{ opacity: 0, scale: 0.6 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.6 }}
                                            transition={{ duration: 0.3 }}
                                            class="col-span-5"
                                            >
                                            <pre><code class="hljs language-python" innerHTML={getHighlightedCode(item.code)}></code></pre>
                                            </Motion.div>
                                    </Show>
                                </Presence>
                                <Presence>
                                    <Show when={showLogs() === item.id}>
                                            <Motion.div
                                            initial={{ opacity: 0, scale: 0.6 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            exit={{ opacity: 0, scale: 0.6 }}
                                            transition={{ duration: 0.3 }}
                                            class="col-span-5"
                                            >
                                            {item.logs ? (
                                                <pre><code class="hljs">{item.logs}</code></pre>
                                            ):(
                                                <pre><code class="hljs text-red-600">No logs available for this submission.</code></pre>
                                            )}
                                            </Motion.div>
                                    </Show>
                                </Presence>
                            </div>
                        )}
                    </For>
                                
                </div>
            </div>
            <div class="flex justify-between items-center">
            <button onClick={toggleControls} type="button" class={`${controlIsActive() ? 'text-white bg-yellow-400': 'text-yellow-400 bg-white hover:text-white'} duration-300 ease-in border-2 border-yellow-400 hover:bg-yellow-400 font-medium rounded-full text-sm px-5 py-2.5 text-center mr-2 mb-2 dark:focus:ring-yellow-900`}>Manual Controls: {controlIsActive() ? 'Activated': "Deactivated"}</button>
            <svg onClick={userSubmissionRefetch} class="hover:cursor-pointer w-6 h-6 text-gray-800 dark:text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 18 20">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 1v5h-5M2 19v-5h5m10-4a8 8 0 0 1-14.947 3.97M1 10a8 8 0 0 1 14.947-3.97"/>
            </svg>

            </div>
            <p class="my-10">Current status: <span class="font-bold">{robotState()}</span></p>

        </div>
    )
}


export default SubmissionList
