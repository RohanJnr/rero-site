import {createSignal} from "solid-js";
import { app } from "../firebasestuff/client";
import { getFirestore, collection, query, where, getDocs, onSnapshot } from "firebase/firestore";


const db = getFirestore(app);
const submissionQuery = query(collection(db, "submissions"), where("submitted_by", "==", "roalleti@gmail.com"));

const querySnapshot = await getDocs(submissionQuery)
const data = []
querySnapshot.forEach((doc) => {
    const doc_data = doc.data()
    const date = new Date(doc_data.datetime_iso);
    console.log(date)
    doc_data["date"] = date.toLocaleString()
    data.push({id: doc.id, ...doc_data})
});


function SubmissionList() {

    return (
        <div>
            <div class="my-10 border-2">
                <div class="grid grid-cols-6 font-medium gap-5 border-2 p-3">
                    <p class="justify-self-center">Submission ID</p>
                    <p class="justify-self-center">Submitted At</p>
                    <p class="justify-self-center">Submitted By</p>
                    <p class="justify-self-center">Code</p>
                    <p class="justify-self-center">Logs</p>
                    <p class="justify-self-center">Actions</p>
                </div>
                <For each={data}>
                    {(item) => (
                    <div class="grid grid-cols-6 gap-5 border-2 p-3">
                        <p class="flex justify-center items-center">{item.id}</p>
                        <p class="flex justify-center items-center">{item.date}</p>
                        <p class="flex justify-center items-center">{item.submitted_by}</p>
                        <p class="flex justify-center items-center gap-2 text-blue-600">View Code <svg class="w-4 h-4 text-blue-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 8">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 5.326 5.7a.909.909 0 0 0 1.348 0L13 1"/>
                        </svg></p>
                        <p class="flex justify-center items-center gap-2 text-blue-600">View Logs <svg class="w-4 h-4 text-blue-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 8">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 5.326 5.7a.909.909 0 0 0 1.348 0L13 1"/>
                        </svg></p>
                        <div class="flex justify-center items-center gap-5">
                        <button class='px-3 py-2 text-sm bg-text-heading text-white rounded font-medium shadow-lg shadow-secondary'>Run</button>
                        </div>
                    </div>
                    )}
                </For>
            </div>
        </div>
    )
}

export default SubmissionList
