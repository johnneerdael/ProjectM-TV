    if (m_warpShader && std::getenv("PROJECTM_RAW_ROUTE_LOG"))
    {
        static int routeFrame=0;
        GLint program=0,active=0;glGetIntegerv(GL_CURRENT_PROGRAM,&program);glGetIntegerv(GL_ACTIVE_TEXTURE,&active);
        GLint flip=0;const GLint flipLocation=glGetUniformLocation(program,"projectm_point_main_flip");if(flipLocation>=0)glGetUniformiv(program,flipLocation,&flip);
        if(flip!=int(presetState.rawPointMainFlip))throw std::runtime_error("research raw orientation uniform mismatch");
        FILE* log=std::fopen(std::getenv("PROJECTM_RAW_ROUTE_LOG"),"a");
        for(const auto* name:{"main","fw_main","pc_main","pw_main"}) {
            const std::string uniform=std::string("sampler_")+name;GLint location=glGetUniformLocation(program,uniform.c_str());
            if(location<0)continue;
            GLint unit=0,texture=0,sampler=0,expectedSampler=0,min=0,mag=0,wrapS=0,wrapT=0;
            glGetUniformiv(program,location,&unit);glActiveTexture(GL_TEXTURE0+unit);glGetIntegerv(GL_TEXTURE_BINDING_2D,&texture);
            glGetIntegerv(GL_SAMPLER_BINDING,&sampler);
            auto expected=presetState.renderContext.textureManager->GetSampler(name);expected->Bind(unit);
            glGetIntegerv(GL_SAMPLER_BINDING,&expectedSampler);glBindSampler(unit,sampler);
            glGetSamplerParameteriv(sampler,GL_TEXTURE_MIN_FILTER,&min);glGetSamplerParameteriv(sampler,GL_TEXTURE_MAG_FILTER,&mag);
            glGetSamplerParameteriv(sampler,GL_TEXTURE_WRAP_S,&wrapS);glGetSamplerParameteriv(sampler,GL_TEXTURE_WRAP_T,&wrapT);
            const GLuint target=std::string(name)=="main" ? presetState.mainTexture.lock()->TextureID() : presetState.rawPointMainTexture.lock()->TextureID();
            const bool okay=GLuint(texture)==target && sampler==expectedSampler && min==expected->FilterMode() && mag==expected->FilterMode() && wrapS==expected->WrapMode() && wrapT==expected->WrapMode();
            if(routeFrame==0||routeFrame==120)std::fprintf(log,"%d,%s,%d,%d,%u,%d,%d,%d,%d,%d,%d,%d,%d\n",routeFrame,name,unit,texture,target,sampler,expectedSampler,min,mag,wrapS,wrapT,presetState.rawPointMainFlip,okay);
            if(!okay)throw std::runtime_error("research source routing mismatch");
        }
        std::fclose(log);glActiveTexture(active);routeFrame++;
    }
