function myFunction() {
    let x = document.getElementById("myDIV");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function spoiler() {
    document.getElementById("contact-form").submit();
}

function myReply(pk) {

    let x = document.getElementById("myReply" + pk);
    if (x.style.display === "none") {
        document.getElementById("comment_div").style.display = "none" ;
        x.style.display = "block";
    } else {
        document.getElementById("comment_div").style.display = "block" ;
        x.style.display = "none";
    }
}

function Reply(pk) {

    let x = document.getElementById("Reply" + pk);
    if (x.style.display === "none") {
        document.getElementById("comment_div").style.display = "none" ;
        x.style.display = "block";
    } else {
        document.getElementById("comment_div").style.display = "block" ;
        x.style.display = "none";
    }
}

