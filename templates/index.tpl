<!DOCTYPE html>
<html>
    <!-- The file in site/index.html is autogenerated using the template in src/templates/index.html! -->
  <head>
      <script type="text/javascript" src="https://d3js.org/d3.v5.min.js"></script>
      <script type="text/javascript" src="https://d3js.org/d3-color.v1.min.js"></script>
      <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min.js"></script>
      <!-- https://lodash.com/docs/4.17.15#template -->
      <!-- ======= This was auto generated: ======= -->
      <% _.each(htmlWebpackPlugin.files.js, function(f) { %>
      <script type="text/javascript" src="<%= f %>"></script>
      <% }); %>
      <!-- ======================================== -->
  </head>
  <body>
      <div>
          <%= VERSION %>
          <%= COMMITHASH %>
          <%= BRANCH %>
      </div>
      <script type="text/javascript">
        const radius = 100;
        const maxLevels = 2;
        const size = maxLevels * 4;
        const background_theme = {
            // "background": "RGBA(118,215,196,0.9)", // turquise
            "background": "RGBA(0,0,0,0.9)", // black
        };
        const line_theme = {
           // "fill": "RGBA(118,215,196,0.5)",
           // "fill": "RGBA(118,215,196,0.75)",
           "stroke": "RGB(244,208,63)",  // Gold
           "stroke": "RGB(192,192,192)", // Silver
           "stroke-width": "7",
       };

        // sacredPatterns.drawDifferentPolygons("d1", radius,  size);
        sacredPatterns.drawStarGrid("d2", radius, size);
        sacredPatterns.drawRotatedStar("d3", radius, size);
        sacredPatterns.drawDifferentStars("d4", radius, size);
        sacredPatterns.drawRotatingCircles("d5", radius, size);
        sacredPatterns.drawHexagonWithSurroundingNonagons("d6", radius, size, background_theme, line_theme);
        sacredPatterns.drawCirclesRecursively("d7", radius, size, maxLevels);

      </script>
  </body>
</html>
