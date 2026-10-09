#pragma once
#include <vector>
#include <array>
#include <cstring>
#include <cstdint>
static std::vector<unsigned char> BufferBytes(GLenum target,GLuint id){GLint previous{};glGetIntegerv(target==GL_ARRAY_BUFFER?GL_ARRAY_BUFFER_BINDING:GL_ELEMENT_ARRAY_BUFFER_BINDING,&previous);glBindBuffer(target,id);GLint size{};glGetBufferParameteriv(target,GL_BUFFER_SIZE,&size);Check(size>0,"nonempty producer buffer");const auto*data=static_cast<const unsigned char*>(glMapBufferRange(target,0,size,GL_MAP_READ_BIT));Check(data,"producer buffer mapping");std::vector<unsigned char> out(data,data+size);Check(glUnmapBuffer(target)==GL_TRUE,"producer buffer unmap");glBindBuffer(target,GLuint(previous));return out;}
struct Attribute {
 GLuint buffer{};size_t offset{},stride{};GLint components{},divisor{};
 std::vector<unsigned char> bytes;
 Attribute(GLuint location){GLint enabled{},type{},bufferId{},strideBytes{};void*pointer{};glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);Check(enabled==GL_TRUE,"producer attribute must be enabled");glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_SIZE,&components);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&strideBytes);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&bufferId);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_DIVISOR,&divisor);glGetVertexAttribPointerv(location,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);Check(type==GL_FLOAT&&bufferId>0,"float producer attribute buffer");buffer=GLuint(bufferId);offset=reinterpret_cast<uintptr_t>(pointer);stride=strideBytes?size_t(strideBytes):size_t(components)*sizeof(float);bytes=BufferBytes(GL_ARRAY_BUFFER,buffer);}
 float Component(size_t row,size_t column)const{Check(column<size_t(components)&&offset+row*stride+(column+1)*sizeof(float)<=bytes.size(),"producer attribute bounds");float value;std::memcpy(&value,bytes.data()+offset+row*stride+column*sizeof(float),sizeof(float));return value;}
 RGBA Color(size_t row)const{Check(components==4,"RGBA producer components");return{Component(row,0),Component(row,1),Component(row,2),Component(row,3)};}
};
