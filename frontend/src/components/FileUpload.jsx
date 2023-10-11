import {createSignal} from "solid-js";

function FileUpload() {

    const [file, setFile] = createSignal()
    const [submitDisabled, setSubmitDisabled] = createSignal(true)

    function onFileUpload(e) {
        console.log("file uploaded")
        const uploadedFile = e.target.files[0]



        if (!uploadedFile.name.endsWith(".py")) {
            alert("Please upload a python file only!")
            return
        }
        setFile(uploadedFile)
        setSubmitDisabled(false)
    }

    function onSubmit(e) {
        console.log("submitted")
    }

    return (
        <div>
            <div class="flex items-center justify-center w-full">
                <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-white">
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                        <svg class="w-8 h-8 mb-4 text-text-light" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                        </svg>
                        <p class="mb-2 text-sm text-text-light"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                        <p class="text-xs text-text-light">Python file ONLY</p>
                        
                        <p class="mt-5">{file() ? <svg class="w-6 h-6 text-green-800" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"/>
  </svg>: ''}</p>
                        <p class="text-text-light">{file() ? `${file().name} Uploaded ` : ''}</p>
                        <p class="text-text-light">{file() ? `${file().size} Bytes` : ''}</p>
                    </div>
                    <input onChange={onFileUpload} id="dropzone-file" type="file" class="hidden" />
                </label>
            </div>

            <button onclick={onSubmit} disabled={submitDisabled()} class={`my-10 px-4 py-4 text-white rounded font-medium ${submitDisabled() ? 'bg-gray-500':'bg-text-heading shadow-lg shadow-secondary'}`}>Submit to Run Code</button>
        </div>
    )
}

export default FileUpload
