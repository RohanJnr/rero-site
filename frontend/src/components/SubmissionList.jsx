import {createResource, createSignal, createEffect} from "solid-js";
import { app } from "../firebasestuff/client";
import { getFirestore, collection, query, where, getDocs, orderBy } from "firebase/firestore";
import { Motion, Presence } from "@motionone/solid";

import hljs from 'highlight.js'
import "highlight.js/styles/stackoverflow-light.css";

function SubmissionList(props) {

    const {user} = props

    const [showCode, setShowCode] = createSignal("")

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

    const [data] = createResource(fetchUserSubmissions)

    const toggleCode = id => {
        if (showCode() === id) {
            setShowCode("")
        }
        else {
            setShowCode(id)
        }
    }

    const getHighlightedCode = (code) => {
        const result = hljs.highlight(code, {language: "python"})
        console.log(result.value)
        return result.value
    }

    const runSubmission = async (submission_id) => {
        const payload = {
            submission_id,
            user_email: user.email
        }

        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const res = await fetch("http://localhost:8000/api/submission/run", {
            method: "POST",
            body: JSON.stringify(payload),
            headers: myHeaders
        })

        const jsonRes = await res.json()
        console.log(jsonRes)
    }

    const stopSubmission = async (submission_id) => {
        const payload = {
            submission_id,
            user_email: user.email
        }

        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const res = await fetch("http://localhost:8000/api/submission/stop", {
            method: "POST",
            body: JSON.stringify(payload),
            headers: myHeaders
        })

        const jsonRes = await res.json()
        console.log(jsonRes)
    }

    return (
        <div>
            <div class="my-10">
                        <div class="relative overflow-x-auto shadow-md sm:rounded-lg">
                            <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
                                <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                                    <tr>
                                        <th scope="col" class="px-6 py-3">
                                            Submission ID
                                        </th>
                                        <th scope="col" class="px-6 py-3">
                                            Submitted Timestamp
                                        </th>
                                        <th scope="col" class="px-6 py-3">
                                            Submitted by
                                        </th>
                                        <th scope="col" class="px-6 py-3">
                                            Code & Logs
                                        </th>
                                        <th scope="col" class="px-6 py-3">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                <For each={data()}>
                                {(item) => (
                                    <>
                                    <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                                        <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">
                                            {item.id}
                                        </th>
                                        <td class="px-6 py-4">
                                            {item.timestamp.toDate().toString().replace(/ GMT\+\d{4} \(India Standard Time\)/, '')}
                                        </td>
                                        <td class="px-6 py-4">
                                            {item.submitted_by}
                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="flex justify-start items-center gap-2">
                                                <p onClick={() => toggleCode(item.id)} class="hover:cursor-pointer font-medium text-blue-600 dark:text-blue-500 hover:underline">Code</p>
                                                <p class="font-medium text-blue-600 dark:text-blue-500 hover:underline hover:cursor-pointer">Logs</p>
                                            </div>

                                        </td>
                                        <td class="px-6 py-4">
                                            <div class="flex justify-start items-center gap-2">
                                                <button onClick={() => runSubmission(item.id)} type="button" class="text-white bg-gradient-to-r from-cyan-500 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-cyan-300 dark:focus:ring-cyan-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2">Run</button>
                                                <button onClick={() => stopSubmission(item.id)} class="relative inline-flex items-center justify-center p-0.5 mb-2 mr-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-red-200 via-red-300 to-yellow-200 group-hover:from-red-200 group-hover:via-red-300 group-hover:to-yellow-200 dark:text-white dark:hover:text-gray-900 focus:ring-4 focus:outline-none focus:ring-red-100 dark:focus:ring-red-400">
                                                  <span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-opacity-0">
                                                      Stop
                                                  </span>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                        <Presence>

                                            <Show when={showCode() === item.id}>
                                                  <Motion.div
                                                    initial={{ opacity: 0, scale: 0.6 }}
                                                    animate={{ opacity: 1, scale: 1 }}
                                                    exit={{ opacity: 0, scale: 0.6 }}
                                                    transition={{ duration: 0.3 }}
                                                  >
                                                    <pre><code class="hljs language-python" innerHTML={getHighlightedCode(item.code)}></code></pre>
                                                  </Motion.div>
                                            </Show>

                                        </Presence>
                                    </>
                                )}
                                </For>
                                </tbody>
                            </table>
                        </div>
            </div>
        </div>
    )
}


export default SubmissionList
