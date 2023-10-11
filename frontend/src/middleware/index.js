import { app } from "../firebasestuff/server";
import { getAuth } from "firebase-admin/auth";


export async function onRequest ({ locals, request, cookies }, next) {

    const auth = getAuth(app);
    locals.user = null

    if (cookies.has("session")) {
        const sessionCookie = cookies.get("session").value;
        const decodedCookie = await auth.verifySessionCookie(sessionCookie);
        const user = await auth.getUser(decodedCookie.uid);

        if (user) {
            locals.user = user
        }
    }
    

    return next();
};