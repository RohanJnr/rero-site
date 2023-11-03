import {createSignal} from "solid-js";
import type { JSX } from 'solid-js';

interface SubmissionData {
    submission_id: string;
    submitted_by: string;
    submitted_by_email: string;
    code: string;
    robot: string;
    team: string;
    datetime_iso: string;
    status: string

}

function FileUpload(props) {
    
    const {robot, user} = props

    const [file, setFile] = createSignal<File>()
    const [submitDisabled, setSubmitDisabled] = createSignal(true)
    const [submitLoading, setSubmitLoading] = createSignal(false)
    const [currentSubmission, setCurrentSubmission] = createSignal<SubmissionData>()

    const onFileUpload: JSX.ChangeEventHandlerUnion<HTMLInputElement, Event> = (e) => {
        if (!e.target.files || e.target.files.length === 0) {
            return
        }
        const uploadedFile = e.target.files[0]

        if (!uploadedFile.name.endsWith(".py")) {
            alert("Please upload a python file only!")
            return
        }

        setFile(uploadedFile)
        setSubmitDisabled(false)
    }

    async function onSubmit() {
        if (!file()) {
            return
        }
        setSubmitLoading(true)
        // @ts-ignore
        const code = await file().text()
        const payload = {
            "robot": robot.name,
            "submitted_by": user.displayName,
            "submitted_by_email": user.email,
            code
        }


        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const res = await fetch("https://server.ieeeraspesu.tech/api/submission/submit", {
            method: "POST",
            body: JSON.stringify(payload),
            headers: myHeaders
        })

        if (res.status !== 200) {
            const jsonRes = await res.json()
            alert(`Something went wrong, try again later or contact us: ${jsonRes.detail}`)
            setSubmitLoading(false)
            return
        }

        const jsonRes = await res.json()
        setCurrentSubmission(JSON.parse(jsonRes))
        setSubmitLoading(false)
    }

    return (
        <div>
            <div class="flex items-center justify-center w-full">
                <label for="dropzone-file" class="shadow-lg flex flex-col items-center justify-center w-full h-64 rounded-lg cursor-pointer bg-white">
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                        <svg class="w-8 h-8 mb-4 text-text-light" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                        </svg>
                        <p class="mb-2 text-sm text-text-light"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                        <p class="text-xs text-text-light">Python file ONLY</p>
                        
                        <p class="mt-5">{file() ? <svg class="w-6 h-6 my-2 text-green-600" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"/>
  </svg>: ''}</p>
                        <p class="text-text-light text-sm">{file() ? `${file().name} Uploaded ` : ''}</p>
                        <p class="text-text-light text-sm">{file() ? `${file().size} Bytes` : ''}</p>
                    </div>
                    <input onChange={onFileUpload} id="dropzone-file" type="file" class="hidden" />
                </label>
            </div>
            <Show
                when={submitLoading()}
                fallback={<button onclick={onSubmit} disabled={submitDisabled()} class={`my-10 text-white dark:focus:ring-green-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 ${submitDisabled() ? 'bg-gray-300':'shadow-lg shadow-green-500/50 bg-gradient-to-r from-green-400 via-green-500 to-green-600 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-green-300'}`}>Submit Code</button>}
            >
                <div role="status" class="my-10">
                    <svg aria-hidden="true" class="w-8 h-8 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                        <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
                    </svg>
                    <span class="sr-only">Loading...</span>
                </div>
            </Show>


            <Show
                when={currentSubmission()}
            >
                <div class="fixed top-0 left-0 right-0 bottom-0 z-50 w-full flex justify-center items-center bg-[#54376b44] p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-[calc(100%-1rem)] max-h-full">
                    <div class="relative w-full max-w-2xl max-h-full">
                        <div class="relative bg-white rounded-lg shadow">
                            <div class="flex items-start justify-between p-4 border-b rounded-t">
                                <h3 class="text-xl font-semibold text-gray-900">
                                    Successful Submission!
                                </h3>
                                <button type="button" class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ml-auto inline-flex justify-center items-center" data-modal-hide="defaultModal">
                                    <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                                    </svg>
                                    <span class="sr-only">Close modal</span>
                                </button>
                            </div>
                            <div class="p-6 space-y-6">
                                <p class="text-base leading-relaxed text-gray-500">
                                    Your code has been submitted and stored successfully on the server with the submission ID <span class="bg-gray-100 p-1 mx-1 rounded text-primary">{currentSubmission()?.submission_id}</span>. This doesn't mean that your code is executing now.
                                </p>
                                <p class="text-base leading-relaxed text-gray-500">

                                </p>
                                <p class="text-base leading-relaxed text-gray-500">
                                    To execute the code, click on the <code>Execute</code> button beside your submissions in the submission table after refreshing this page.
                                </p>
                            </div>
                            <div onClick={() => window.location.reload()} class="flex items-center p-6 space-x-2 border-t border-gray-200 rounded-b">
                                <button data-modal-hide="defaultModal" type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center">Refresh</button>
                            </div>
                        </div>
                    </div>
                </div>
            </Show>

        </div>

        
    )
}

export default FileUpload
