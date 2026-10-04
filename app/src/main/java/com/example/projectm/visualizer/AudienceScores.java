package com.example.projectm.visualizer;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/** Review-only score table; intensity and collection-relative rank stay distinct. */
final class AudienceScores {
    private final Map<String,double[]> rows=new HashMap<>();
    static AudienceScores read(Reader reader) throws IOException {
        AudienceScores result=new AudienceScores();
        try(BufferedReader input=new BufferedReader(reader)) {
            String line;
            while((line=input.readLine())!=null) {
                String[] parts=line.split("\t",-1);
                if(parts.length!=3||parts[0].isEmpty())throw new IllegalArgumentException("Invalid audience score row");
                double score=Double.parseDouble(parts[1]),rank=Double.parseDouble(parts[2]);
                if(Double.isNaN(score)||Double.isInfinite(score)||Double.isNaN(rank)||Double.isInfinite(rank)||score<0||score>100||rank<1||rank>100||result.rows.containsKey(parts[0]))
                    throw new IllegalArgumentException("Invalid or duplicate audience score");
                result.rows.put(parts[0],new double[]{score,rank});
            }
        }
        return result;
    }
    String describe(String preset) {
        double[] value=rows.get(preset);
        return value==null?"Score unavailable":String.format(Locale.US,"Score %.1f / 100 · rank %.1f / 100",value[0],value[1]);
    }
}
