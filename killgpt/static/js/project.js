/* Project specific Javascript goes here. */
<script>
    window.onload = function() {
        document.getElementById("loading-screen").style.display = "none";
    };
    window.onbeforeunload = function() {
        document.getElementById("loading-screen").style.display = "block";
    };
</script>