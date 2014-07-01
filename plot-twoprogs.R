# args: pngout base-title head-title base-json head-json
library(rjson)
library(ggplot2)

args <- commandArgs(trailingOnly = TRUE)
draw.plot <- function(d1, d2) {
    name <- "compiling stage2 librustc"
    dat1 <- data.frame(t(as.data.frame(d1$memory_data)))
    dat1[,2] <- dat1[,2]/(1024**2)
    dat2 <- data.frame(t(as.data.frame(d2$memory_data)))
    dat2[,2] <- dat2[,2]/(1024**2)

    row.names(dat1) <- c()
    row.names(dat2) <- c()
    names(dat1) <- c("time", "mem")
    names(dat2) <- c("time", "mem")
	
    dat1 <- cbind(dat1, dat=args[2])
	cat(args[2])
    dat2 <- cbind(dat2, dat=args[3])
	cat(args[3])
    dat <- rbind(dat1, dat2)
    dat$dat <- factor(dat$dat)

	cat(args[1])
    png(args[1], width=1024, height=1024)

    print(qplot(time, mem, data=dat, colour=dat, geom="line",  main=name, xlab="Time (s)", ylab="Memory (MiB)"))
    dev.off()
}

cat(args[4])
data <- fromJSON(file=args[4])
cat(args[5])
data2 <- fromJSON(file=args[5])
draw.plot(data, data2)
