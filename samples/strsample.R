alph4 = letters[1:4]
alph16 = letters[1:16]
alph64 = c(letters, LETTERS, 0:9, '#', '$')

for (i in c('4', '16', '64')) {
     filename = paste('samples/alph', i, '_sample.txt',sep='')
     alph = get(paste('alph',i,sep=''))
     cat(alph, file=filename, sep="\n")
     if (i=='4' || i=='16') {
          C = apply(expand.grid(alph, alph), 1, paste)
          cat(paste(C[1,], C[2,], sep=''), file=filename, sep="\n", append=TRUE)
          if (i=='4') {
               C = apply(expand.grid(alph, alph, alph), 1, paste)
               cat(paste(C[1,], C[2,], C[3,], sep=''), file=filename,
                   sep="\n", append=TRUE)
               C = apply(expand.grid(alph, alph, alph, alph), 1, paste)
               cat(paste(C[1,], C[2,], C[3,], C[4,], sep=''), file=filename,
                   sep="\n", append=TRUE)
          }
     }
     strt.idx = list('4'=5, '16'=3, '64'=2)[[i]]
     for (j in strt.idx:100) {
          cat('Sampling strings of length', j, 'in alphabet', i, '\n')
          strlist = c()
          while (length(strlist) < 1000) {
               smpl = paste(sample(alph, size=j, replace=TRUE), collapse='')
               if (smpl %in% strlist) next
               strlist = c(strlist, smpl)
          }
          cat(strlist, file=filename, sep="\n", append=TRUE)
     }
}

check.num.lines = function(filename) {
     f <- file(filename, open="r")
     nlines = 0L
     while (TRUE) {
          line = readLines(f, n=1)
          if (length(line) == 0) break
          nlines = nlines + 1
     }
     close(f)
     cat(filename, 'has', nlines, 'lines\n')
}

check.num.lines('samples/alph4_sample.txt')
check.num.lines('samples/alph16_sample.txt')
check.num.lines('samples/alph64_sample.txt')
