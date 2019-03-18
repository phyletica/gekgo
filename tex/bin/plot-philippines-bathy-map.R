#! /usr/bin/env Rscript

library(maps)
library(mapdata)
library(ggplot2)
library(marmap)
library(viridis)

point_size = 2.7
legend_point_size = 4.0
legend_point_shape = 15
legend_title_font_size = 14.0
legend_label_font_size = 14.0
label_font_size = 28.0
line_size = 1.9
pgreen = rgb(50, 162, 81, max = 255)
porange = rgb(255, 127, 15, max = 255)
pblue = rgb(60, 183, 204, max = 255)
pyellow = rgb(255, 217, 74, max = 255)
pteal = rgb(57, 115, 124, max = 255)
pauburn = rgb(184, 90, 13, max = 255)

# How I got these colors from matplotlib:
# import matplotlib
# v = matplotlib.cm.get_cmap("viridis")
# v(0.0, bytes = True)
viridis00 = rgb(68, 1, 84, max = 255)
# v(0.5, bytes = True)
viridis05 = rgb(32, 144, 140, max = 255)
# v(1.0, bytes = True)
viridis10 = rgb(253, 231, 36, max = 255)


# connected_color = pauburn
# maybe_connected_color = pgreen
# not_connected_color = pteal
connected_color = viridis00
maybe_connected_color = viridis05 
not_connected_color = viridis10

get_color = function(x) {
    if (x == "yes") {
        return(connected_color)
    }
    else if (x == "no") {
        return(not_connected_color)
    }
    else {
        return(maybe_connected_color)
    }
}

sea_level_data = read.delim(
        "spratt2016-sea-level-projection.txt",
        header=T,
        sep="\t",
        skip=95)
# Combine sea level projection from 0-430k years ago with projection from
# 430k-798k years ago
sea_levels = c(sea_level_data$SeaLev_shortPC1[0:431], sea_level_data$SeaLev_longPC1[-0:-431])
sea_level_data$sealevel = sea_levels

bathy_raw_data = getNOAA.bathy(
        lon1 = 116,
        lon2 = 126.5,
        lat1 = 5,
        lat2 = 21,
        resolution = 1,
        keep = T)
bathy_data = fortify.bathy(bathy_raw_data)

points = read.delim("localities.csv", sep = ",", header = TRUE)
points$color = mapply(get_color, points$connected)

gekko_points = subset(points, genus == "Gekko")
cyrt_points = subset(points, genus == "Cyrtodactylus")

d = map_data("worldHires", c("Philippines", "Malaysia", "Indonesia"))

for (depth in seq(0, min(sea_levels), -5)) {
    label = paste(formatC(depth, format = "d", width = 3, flag = " "),
            "m",
            sep = "")

    p = ggplot() +
        # geom_raster(data = bathy_data, aes(x = x, y = y, fill = z),
        #             alpha = 0.3,
        #             show.legend = FALSE) +
        # scale_fill_gradient(limits = c(depth, max(bathy_data)),
        #         low = "black",
        #         high = "black",
        #         na.value = "white") +
        geom_contour(data = bathy_data, aes(x = x, y = y, z = z),
                     breaks = c(depth),
                     size = c(0.3),
                     colour = "black") +
        geom_polygon(data = d, aes(x = long, y = lat, group = group),
                     fill = "gray",
                     ) +
        coord_fixed(xlim = c(116.8, 126.2),
                    ylim = c(6.15, 20.2),
                    ratio = 1.0) +
        theme_minimal(base_size = 14) +
        theme(
                axis.title.x = element_blank(),
                axis.title.y = element_blank(),
        ) +
        # labs(x = "Longitude") +
        # labs(y = "Latitude") +
        geom_label(aes(x = 126.2, y = 20.2,
                      label = label,
                      size = label_font_size,
                      hjust = "right",
                      vjust = "top"),
                  label.size = NA,
                  show.legend = FALSE)
        # geom_point(data = cyrt_points,
        #            aes(x = long1, y = lat1),
        #            color = cyrt_points$color,
        #            size = point_size,
        #            show.legend = FALSE) +
        # geom_point(data = cyrt_points,
        #            aes(x = long2, y = lat2),
        #            color = cyrt_points$color,
        #            size = point_size,
        #            show.legend = FALSE) +
        # geom_segment(data = cyrt_points,
        #              aes(x = long1, y = lat1,
        #                  xend = long2, yend=lat2),
        #              color = cyrt_points$color,
        #              size = line_size,
        #              show.legend = FALSE) +
        # geom_text(data = cyrt_points,
        #           aes(x = long1, y = lat1,
        #               label = as.character(island1),
        #               hjust = as.character(hjust1),
        #               vjust = as.character(vjust1)),
        #           nudge_x = cyrt_points$nudge_x1,
        #           nudge_y = cyrt_points$nudge_y1,
        #           show.legend = FALSE) +
        # geom_text(data = cyrt_points,
        #           aes(x = long2, y = lat2,
        #               label = as.character(island2),
        #               hjust = as.character(hjust2),
        #               vjust = as.character(vjust2)),
        #           nudge_x = cyrt_points$nudge_x2,
        #           nudge_y = cyrt_points$nudge_y2,
        #           show.legend = FALSE)

    plot_path = paste(
            "../images/bathymetry-maps/",
            "depth-",
            formatC(abs(depth), format = "d", width = 3, flag = 0),
            "m.pdf",
            sep = "")
    
    ggsave(plot_path, width = 5.0, height = 7.0, units = "in")
}
