void MilkdropShader::CompileAcidSidecar(const std::string& vertex,const std::string& fragment)
{
    if(!std::getenv("PROJECTM_ACID_DIAG_LOG")) return;
    std::ofstream(std::string(std::getenv("PROJECTM_ACID_DIAG_LOG"))+(m_type==ShaderType::WarpShader ? ".primary.glsl" : ".comp.primary.glsl")) << fragment;
    const auto source=AcidSidecarSource(fragment);
    if(source.empty()) return;
    std::ofstream(std::string(std::getenv("PROJECTM_ACID_DIAG_LOG"))+(m_type==ShaderType::WarpShader ? ".sidecar.glsl" : ".comp.sidecar.glsl")) << source;
    m_acidSidecar.CompileProgram(vertex,source);
    m_acidSidecarReady=true;
}

void MilkdropShader::DrawAcidSidecar(int indices,int width,int height)
{
    const int current=m_acidSidecarFrame++;
    if(!m_acidSidecarReady || current%15!=0) return;
    GLint primary=0,draw=0,read=0,viewport[4]{};
    glGetIntegerv(GL_CURRENT_PROGRAM,&primary);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_VIEWPORT,viewport);
    const int W=std::getenv("PROJECTM_ACID_DIAG_GRID") ? std::atoi(std::getenv("PROJECTM_ACID_DIAG_GRID")) : 128;
    const int H=W*9/16;
    static GLuint fbo=0,tex=0;
    if(!fbo) {
        GLint active=0,binding=0;glGetIntegerv(GL_ACTIVE_TEXTURE,&active);glActiveTexture(GL_TEXTURE0);
        glGetIntegerv(GL_TEXTURE_BINDING_2D,&binding);
        glGenTextures(1,&tex);glBindTexture(GL_TEXTURE_2D,tex);
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,W,H,0,GL_RGBA,GL_FLOAT,nullptr);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);
        glBindTexture(GL_TEXTURE_2D,binding);glActiveTexture(active);
        glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex,0);
        if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE) throw std::runtime_error("sidecar incomplete FBO");
    }
    glBindFramebuffer(GL_FRAMEBUFFER,fbo);glViewport(0,0,W,H);
    const GLenum buffer=GL_COLOR_ATTACHMENT0;glDrawBuffers(1,&buffer);glReadBuffer(buffer);
    m_acidSidecar.Bind();GLint diagnostic=0;glGetIntegerv(GL_CURRENT_PROGRAM,&diagnostic);
    AcidCopyUniforms(primary,diagnostic);
    glUniform4f(glGetUniformLocation(diagnostic,"acid_diag_lattice"),width,height,1182,665);
    const auto location=glGetUniformLocation(diagnostic,"acid_diag_mode");
    std::vector<float> pixels(W*H*4),phases,advection;
    FILE* log=std::fopen(std::getenv("PROJECTM_ACID_DIAG_LOG"),"a");
    if(!log)throw std::runtime_error("sidecar log failed");
    for(int mode=m_type==ShaderType::WarpShader ? 1 : 8;mode<=(m_type==ShaderType::WarpShader ? 7 : 12);mode++) {
        glUniform1i(location,mode);glDrawElements(GL_TRIANGLES,indices,GL_UNSIGNED_INT,nullptr);
        glReadPixels(0,0,W,H,GL_RGBA,GL_FLOAT,pixels.data());

        if(mode==1) phases=pixels;
        if(mode==2) advection=pixels;
        if(mode==3) {
            FILE* joint=std::fopen((std::string(std::getenv("PROJECTM_ACID_DIAG_LOG"))+".weighted").c_str(),"a");
            std::fprintf(joint,"%d,%d,%d",current,width,height);
            for(int category=0;category<5;category++) {
                double sum=0,moments[4]{};
                for(int i=0;i<W*H;i++) {
                    double weight;
                    if(category<3)weight=pixels[i*4+category]*pixels[i*4+category];
                    else if(category==3) {
                        const double v=.2126*pixels[i*4]+.7152*pixels[i*4+1]+.0722*pixels[i*4+2];weight=v*v;
                    } else weight=.2126*advection[i*4]+.7152*advection[i*4+1]+.0722*advection[i*4+2];
                    if(!std::isfinite(weight))continue;sum+=weight;
                    for(int c=0;c<4;c++){const double f=phases[i*4+c];if(std::isfinite(f))moments[c]+=weight*f*(1-f);}
                }
                std::fprintf(joint,",%.12g",sum/double(W*H));
                for(double value:moments)std::fprintf(joint,",%.12g",value/std::max(1e-30,sum));
            }
            std::fprintf(joint,"\n");std::fclose(joint);
        }

        std::fprintf(log,"%d,%d,%d,%d",current,width,height,mode);
        for(int c=0;c<4;c++) {
            double sum=0,var=0,clip=0,neg=0,pos=0;float lo=1e30f,hi=-1e30f;int finite=0,below=0,above=0;
            for(int i=0;i<W*H;i++) {
                const float x=pixels[i*4+c];if(!std::isfinite(x))continue;
                sum+=x;var+=x*(1-x);clip+=std::clamp(x,0.0f,1.0f);neg+=std::max(0.0f,-x);pos+=std::max(0.0f,x-1);lo=std::min(lo,x);hi=std::max(hi,x);finite++;below+=x<0;above+=x>1;
            }
            const double count=std::max(1,finite);
            std::fprintf(log,",%.12g,%.12g,%.12g,%.12g,%.12g,%.12g,%.12g",sum/count,var/count,lo,hi,below/count,above/count,1-finite/double(W*H));
            std::fprintf(log,",%.12g,%.12g,%.12g",clip/count,neg/count,pos/count);
        }
        std::fprintf(log,"\n");
    }
    std::fclose(log);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glBindFramebuffer(GL_READ_FRAMEBUFFER,read);
    glViewport(viewport[0],viewport[1],viewport[2],viewport[3]);m_shader.Bind();
}

