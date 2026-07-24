/* =====================================
   AZ TURF PRO V6
   DESIGN HIPPIQUE PREMIUM
===================================== */


*{
    box-sizing:border-box;
    font-family:Arial, Helvetica, sans-serif;
}


body{

    margin:0;
    background:#0b1712;
    color:white;

}


/* =====================
 HEADER
===================== */


.header-az{

    background:#06351f;
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:18px 25px;
    border-bottom:3px solid #d4af37;

}


.logo{

    font-size:26px;
    font-weight:bold;
    color:#d4af37;

}



nav a{

    color:white;
    text-decoration:none;
    padding:10px 15px;
    margin:5px;
    border-radius:8px;

}



nav a:hover{

    background:#d4af37;
    color:#111;

}



/* =====================
 HERO ACCUEIL
===================== */


.hero-az{

    min-height:480px;

    background:

    linear-gradient(
    rgba(0,0,0,.55),
    rgba(0,0,0,.75)
    ),

    url("images/banner.jpg");


    background-size:cover;
    background-position:center;

    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;

}



.overlay{

    padding:20px;

}



.overlay h1{

    font-size:42px;
    color:#d4af37;

}



.overlay p{

    font-size:20px;

}



/* =====================
 COMPTEUR
===================== */


.countdown-box{

    background:rgba(0,0,0,.75);

    border:2px solid #d4af37;

    border-radius:15px;

    padding:20px;

    margin:25px auto;

    max-width:350px;

}



.countdown-box h2{

    color:#d4af37;

}



#countdown{

    font-size:40px;
    font-weight:bold;
    color:#00ff88;

}





/* =====================
 CONTENEUR
===================== */


.container{

    max-width:1200px;

    margin:auto;

    padding:20px;

}




/* =====================
 BLOCS
===================== */


.course-box,
.selection-az,
.ticket-box,
.publicite{

    background:#111d18;

    border-radius:15px;

    padding:25px;

    margin-bottom:25px;

    border:1px solid #28553d;

}



h1,
h2{

    color:#d4af37;

}




/* =====================
 BOUTONS
===================== */


.btn-az{

    display:inline-block;

    background:#087f3d;

    color:white;

    padding:14px 25px;

    border-radius:10px;

    text-decoration:none;

    font-weight:bold;

}



.btn-az:hover{

    background:#d4af37;

    color:#111;

}





/* =====================
 COURSES
===================== */


.grid-courses{

    display:grid;

    grid-template-columns:
    repeat(auto-fit,minmax(220px,1fr));

    gap:15px;

}



.course-card{

    background:#06351f;

    padding:20px;

    border-radius:12px;

    border-left:5px solid #d4af37;

}



.course-card span{

    color:#00ff88;

}




/* =====================
 CHEVAUX
===================== */


.cheval{

    background:#17251e;

    padding:15px;

    margin:12px 0;

    border-radius:12px;

    border-left:5px solid #d4af37;

}



.cheval strong{

    color:#d4af37;

}



.confiance{

    color:#00ff88;

    font-weight:bold;

}




/* =====================
 TICKETS
===================== */


.ticket-box{

    text-align:center;

}



.game-grid{

    display:grid;

    grid-template-columns:
    repeat(auto-fit,minmax(150px,1fr));

    gap:15px;

}



.game-grid div{

    background:#06351f;

    padding:20px;

    border-radius:10px;

    font-weight:bold;

}





/* =====================
 PUBLICITES
===================== */


.pub-slider{

    height:230px;

    position:relative;

    overflow:hidden;

}



.pub-slider img{

    width:100%;

    height:230px;

    object-fit:cover;

    border-radius:12px;

    position:absolute;

    animation:pub 15s infinite;

}



.pub-slider img:nth-child(2){

    animation-delay:5s;

}



.pub-slider img:nth-child(3){

    animation-delay:10s;

}



@keyframes pub{


0%{

opacity:0;

}


10%{

opacity:1;

}


30%{

opacity:1;

}


40%{

opacity:0;

}


100%{

opacity:0;

}


}




/* =====================
 FOOTER
===================== */


footer{

    background:#06351f;

    text-align:center;

    padding:20px;

    margin-top:30px;

    border-top:3px solid #d4af37;

}





/* =====================
 MOBILE
===================== */


@media(max-width:700px){


.header-az{

    flex-direction:column;

}


nav{

    margin-top:15px;

}



nav a{

    display:inline-block;

}



.overlay h1{

    font-size:28px;

}



#countdown{

    font-size:32px;

}



.container{

    padding:10px;

}


   }
